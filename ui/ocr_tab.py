"""تبويب OCR — التعرف الضوئي على الحروف (اختياري حسب تثبيت Tesseract)."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QProgressBar, QFrame,
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import Qt, QUrl

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr, tr_text, tr_fmt
from core.ocr import ocr_pdf, available, OcrError, INSTALL_HINT
from core.history import record

PDF_FILTER = "PDF (*.pdf)"


class OcrTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

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

        opts = QHBoxLayout()
        opts.addWidget(QLabel("اللغة"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("عربي + إنجليزي", "ara+eng")
        self.lang_combo.addItem("عربي فقط", "ara")
        self.lang_combo.addItem("إنجليزي فقط", "eng")
        opts.addWidget(self.lang_combo)

        opts.addWidget(QLabel("الدقة"))
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItem("سريعة (150)", 150)
        self.dpi_combo.addItem("متوازنة (200)", 200)
        self.dpi_combo.addItem("دقيقة (300)", 300)
        self.dpi_combo.setCurrentIndex(1)
        opts.addWidget(self.dpi_combo)
        opts.addStretch()
        layout.addLayout(opts)

        run_layout = QHBoxLayout()
        self.run_btn = QPushButton(tr("run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        run_layout.addStretch()
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
            layout.addStretch()

        layout.addStretch()
        self.src_path = None

    def _on_file(self, paths):
        if not paths:
            return
        self.src_path = paths[0]
        self.status_label.setText(f"📄 {os.path.basename(self.src_path)}")
        self.run_btn.setEnabled(self.avail)
        if not self.avail:
            show_toast(self, "OCR غير مفعّل — راجع خطوات التثبيت أدناه", "warning")

    def _run(self):
        if not self.src_path or self.worker or not self.avail:
            return
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText(tr_text("⏳ جارٍ التعرف على النص (قد يستغرق دقائق للملفات الكبيرة)…"))
        self.worker = Worker(ocr_pdf, self.src_path,
                             os.path.splitext(self.src_path)[0] + "_OCR.pdf",
                             self.lang_combo.currentData(),
                             self.dpi_combo.currentData())
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _on_done(self, result):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        show_toast(self, tr_fmt("✅ أصبح الملف قابلاً للبحث ({pages} صفحة)", pages=result['pages']), "info")
        self.status_label.setText(tr_fmt("✅ محفوظ: {out}", out=result['out']))
        record("OCR", result["out"])

    def _on_fail(self, err):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText(f"❌ {tr_text(err)}")
