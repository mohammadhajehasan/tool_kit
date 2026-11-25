"""تبويب OCR — Tesseract محلياً أو Unlimited-OCR عبر خادم بعيد."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QProgressBar, QFrame, QLineEdit,
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import Qt, QUrl

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr, tr_text, tr_fmt
from core.ocr import ocr_pdf, available, OcrError, INSTALL_HINT
from core import unlimited_ocr as U
from core.history import record

PDF_FILTER = "PDF (*.pdf)"


class OcrTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.conn_worker = None
        self.src_path = None
        self.cfg = U.load_config()
        self._build_ui()

    # ---------- البناء ----------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(tr("ocr_title"))
        title.setObjectName("pageTitle")
        desc = QLabel(tr("ocr_desc"))
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF ممسوح ضوئياً هنا",
            sub_text="الناتج: PDF يحتوي طبقة نص مخفية قابلة للبحث والنسخ",
            file_filter=PDF_FILTER, multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        engine_row = QHBoxLayout()
        engine_row.addWidget(QLabel("المحرك:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("Tesseract (محلي)", "tesseract")
        self.engine_combo.addItem("Unlimited-OCR (خادم)", "unlimited")
        engine_row.addWidget(self.engine_combo)
        engine_row.addStretch()
        layout.addLayout(engine_row)

        # إعدادات خادم Unlimited-OCR
        self.server_box = QFrame()
        self.server_box.setObjectName("aboutCard")
        sv = QVBoxLayout(self.server_box)
        sv.setContentsMargins(16, 12, 16, 12)
        sv.setSpacing(8)

        url_row = QHBoxLayout()
        url_row.addWidget(QLabel("عنوان الخادم:"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("http://127.0.0.1:10000")
        url_row.addWidget(self.url_edit, 1)
        sv.addLayout(url_row)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("اسم النموذج:"))
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("Unlimited-OCR-2")
        model_row.addWidget(self.model_edit, 1)
        sv.addLayout(model_row)

        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("مفتاح API (اختياري)"))
        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.Password)
        self.key_edit.setPlaceholderText("اتركه فارغاً إن لم يكن الخادم يتطلب مفتاحاً")
        key_row.addWidget(self.key_edit, 1)
        sv.addLayout(key_row)

        test_row = QHBoxLayout()
        self.test_btn = QPushButton("فحص الاتصال")
        self.test_btn.setObjectName("secondaryBtn")
        self.test_btn.setCursor(Qt.PointingHandCursor)
        self.test_btn.clicked.connect(self._test_connection)
        test_row.addWidget(self.test_btn)
        test_row.addStretch()
        sv.addLayout(test_row)

        self.conn_label = QLabel("")
        self.conn_label.setObjectName("hintLabel")
        self.conn_label.setWordWrap(True)
        sv.addWidget(self.conn_label)

        layout.addWidget(self.server_box)

        opts = QHBoxLayout()
        self.lang_label = QLabel("اللغة")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("عربي + إنجليزي", "ara+eng")
        self.lang_combo.addItem("عربي فقط", "ara")
        self.lang_combo.addItem("إنجليزي فقط", "eng")
        opts.addWidget(self.lang_label)
        opts.addWidget(self.lang_combo)

        opts.addWidget(QLabel("الدقة"))
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItem("سريعة (150)", 150)
        self.dpi_combo.addItem("متوازنة (200)", 200)
        self.dpi_combo.addItem("دقيقة (300)", 300)
        opts.addWidget(self.dpi_combo)
        opts.addStretch()
        layout.addLayout(opts)

        run_layout = QHBoxLayout()
        self.cancel_btn = QPushButton(tr("cancel"))
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.run_btn = QPushButton(tr("run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        run_layout.addStretch()
        run_layout.addWidget(self.cancel_btn)
        run_layout.addWidget(self.run_btn)
        layout.addLayout(run_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.avail = available()
        self.hint_card = None
        if not self.avail:
            hint = QFrame()
            hint.setObjectName("aboutCard")
            hv = QVBoxLayout(hint)
            hv.setContentsMargins(18, 14, 18, 14)
            t = QLabel("⚙️  OCR غير مفعّل على هذا النظام")
            t.setObjectName("cardTitle")
            b = QLabel(INSTALL_HINT)
            b.setObjectName("cardBody")
            b.setWordWrap(True)
            b.setTextInteractionFlags(Qt.TextBrowserInteraction)
            link = QPushButton("⬇️ تحميل Tesseract OCR")
            link.setObjectName("secondaryBtn")
            link.setCursor(Qt.PointingHandCursor)
            link.clicked.connect(lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/UB-Mannheim/tesseract/wiki")))
            hv.addWidget(t)
            hv.addWidget(b)
            hv.addWidget(link)
            layout.addWidget(hint)
            self.hint_card = hint

        layout.addStretch()

        self._apply_config()
        self.engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        self._on_engine_changed()

    def _apply_config(self):
        cfg = self.cfg
        engine = str(cfg.get("ocr_engine") or "")
        if not engine:
            engine = "unlimited" if (U.is_configured(cfg) and not self.avail) else "tesseract"
        idx = self.engine_combo.findData(engine)
        self.engine_combo.setCurrentIndex(idx if idx >= 0 else 0)

        self.url_edit.setText(str(cfg.get("unlimited_ocr_url") or ""))
        self.model_edit.setText(str(cfg.get("unlimited_ocr_model") or ""))
        self.key_edit.setText(str(cfg.get("unlimited_ocr_api_key") or ""))

        dpi = int(cfg.get("unlimited_ocr_dpi") or 200)
        dpi_idx = self.dpi_combo.findData(dpi)
        if dpi_idx < 0:
            self.dpi_combo.addItem(str(dpi), dpi)
            dpi_idx = self.dpi_combo.count() - 1
        self.dpi_combo.setCurrentIndex(dpi_idx)

    def _is_unlimited(self) -> bool:
        return self.engine_combo.currentData() == "unlimited"

    def _on_engine_changed(self):
        unlimited = self._is_unlimited()
        self.server_box.setVisible(unlimited)
        self.lang_label.setVisible(not unlimited)
        self.lang_combo.setVisible(not unlimited)
        if self.hint_card is not None:
            self.hint_card.setVisible(not unlimited and not self.avail)
        self._refresh_run_state()
        try:
            U.save_config({"ocr_engine": self.engine_combo.currentData()})
        except Exception:
            pass

    def _refresh_run_state(self):
        if self.worker is not None:
            self.run_btn.setEnabled(False)
            return
        if not self.src_path:
            self.run_btn.setEnabled(False)
        elif self._is_unlimited():
            self.run_btn.setEnabled(U.is_configured(self._collect_cfg(save=False)))
        else:
            self.run_btn.setEnabled(self.avail)

    def _collect_cfg(self, save: bool = True) -> dict:
        cfg = dict(self.cfg)
        cfg.update({
            "ocr_engine": self.engine_combo.currentData(),
            "unlimited_ocr_url": self.url_edit.text().strip(),
            "unlimited_ocr_model": self.model_edit.text().strip(),
            "unlimited_ocr_api_key": self.key_edit.text().strip(),
            "unlimited_ocr_dpi": int(self.dpi_combo.currentData() or 200),
        })
        self.cfg = cfg
        if save:
            try:
                U.save_config({
                    "ocr_engine": cfg["ocr_engine"],
                    "unlimited_ocr_url": cfg["unlimited_ocr_url"],
                    "unlimited_ocr_model": cfg["unlimited_ocr_model"],
                    "unlimited_ocr_api_key": cfg["unlimited_ocr_api_key"],
                    "unlimited_ocr_dpi": cfg["unlimited_ocr_dpi"],
                })
            except Exception:
                pass
        return cfg

    # ---------- الأحداث ----------

    def _on_file(self, paths):
        if not paths:
            return
        self.src_path = paths[0]
        self.status_label.setText(f"📄 {os.path.basename(self.src_path)}")
        self._refresh_run_state()
        if self._is_unlimited() and not U.is_configured(self._collect_cfg(save=False)):
            show_toast(self, "أدخل عنوان الخادم واسم النموذج أولاً", "warning")
        elif not self._is_unlimited() and not self.avail:
            show_toast(self, "OCR غير مفعّل — راجع خطوات التثبيت أدناه", "warning")

    def _cancel(self):
        if self.worker:
            self.worker.cancel()

    def _set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.cancel_btn.setVisible(running)
        self.cancel_btn.setEnabled(running)
        self.progress.setVisible(running)
        if not running:
            self._refresh_run_state()

    def _on_progress(self, message: str):
        self.status_label.setText(tr_text(str(message)))

    def _test_connection(self):
        if self.conn_worker is not None:
            return
        cfg = self._collect_cfg()
        if not cfg["unlimited_ocr_url"] or not cfg["unlimited_ocr_model"]:
            show_toast(self, "أدخل عنوان الخادم واسم النموذج أولاً", "warning")
            return
        self.test_btn.setEnabled(False)
        self.conn_label.setText(tr_text("⏳ جارٍ فحص الاتصال…"))
        self.conn_worker = Worker(
            U.check_connection, cfg["unlimited_ocr_url"], cfg["unlimited_ocr_api_key"])
        self.conn_worker.finished_ok.connect(self._conn_ok)
        self.conn_worker.failed.connect(self._conn_fail)
        self.conn_worker.start()

    def _conn_ok(self, info):
        self.conn_worker = None
        self.test_btn.setEnabled(True)
        models = info.get("models") if isinstance(info, dict) else None
        if models:
            self.conn_label.setText(tr_fmt(
                "✅ الخادم متصل — النماذج: {models}", models=", ".join(models[:5])))
        else:
            self.conn_label.setText(tr_text("✅ الخادم متصل"))
        show_toast(self, tr_text("تم الاتصال بالخادم"), "success")

    def _conn_fail(self, err):
        self.conn_worker = None
        self.test_btn.setEnabled(True)
        self.conn_label.setText(tr_fmt("❌ تعذّر الاتصال: {err}", err=tr_text(str(err))))
        show_toast(self, str(err), "error")

    def _run(self):
        if not self.src_path or self.worker is not None:
            return
        cfg = self._collect_cfg()
        if self._is_unlimited():
            if not U.is_configured(cfg):
                show_toast(self, "أدخل عنوان الخادم واسم النموذج أولاً", "warning")
                return
            out_pdf = os.path.splitext(self.src_path)[0] + "_OCR.pdf"
            out_txt = os.path.splitext(self.src_path)[0] + "_OCR.txt"
            self._set_running(True)
            self.status_label.setText(tr_text(
                "⏳ جارٍ استخراج النص عبر Unlimited-OCR (قد يستغرق دقائق)…"))
            self.worker = Worker(
                U.ocr_pdf, self.src_path, out_pdf, out_txt,
                cfg=cfg, dpi=int(self.dpi_combo.currentData() or 200))
        else:
            if not self.avail:
                return
            self._set_running(True)
            self.status_label.setText(tr_text(
                "⏳ جارٍ التعرف على النص (قد يستغرق دقائق للملفات الكبيرة)…"))
            self.worker = Worker(
                ocr_pdf, self.src_path,
                os.path.splitext(self.src_path)[0] + "_OCR.pdf",
                self.lang_combo.currentData(),
                self.dpi_combo.currentData())
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _on_done(self, result):
        self.worker = None
        self._set_running(False)
        if isinstance(result, dict) and "out_txt" in result:
            pages = result.get("pages", 0)
            if result.get("pdf_written"):
                show_toast(self, tr_fmt(
                    "✅ أصبح الملف قابلاً للبحث ({pages} صفحة)", pages=pages), "info")
                self.status_label.setText(
                    tr_fmt("✅ محفوظ: {out}", out=result["out_pdf"])
                    + "\n" + tr_fmt("📝 النص أيضاً في: {out}", out=result["out_txt"]))
            else:
                show_toast(self, tr_fmt(
                    "✅ استُخرج النص ({pages} صفحة)", pages=pages), "info")
                self.status_label.setText(
                    tr_fmt("📝 النص محفوظ في: {out}", out=result["out_txt"]))
            for warning in result.get("warnings") or []:
                self.status_label.setText(self.status_label.text() + "\n⚠️ " + tr_text(warning))
            record("OCR", result.get("out_pdf") or result["out_txt"])
        else:
            show_toast(self, tr_fmt(
                "✅ أصبح الملف قابلاً للبحث ({pages} صفحة)", pages=result['pages']), "info")
            self.status_label.setText(tr_fmt("✅ محفوظ: {out}", out=result['out']))
            record("OCR", result["out"])

    def _on_fail(self, err):
        self.worker = None
        self._set_running(False)
        self.status_label.setText(f"❌ {tr_text(err)}")
