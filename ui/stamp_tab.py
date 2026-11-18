"""تبويب العلامة المائية وترقيم الصفحات."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QProgressBar, QFrame, QFileDialog,
)
from PySide6.QtCore import Qt

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr
from core.stamp import watermark, add_page_numbers, StampError
from core.history import record

PDF_FILTER = "PDF (*.pdf)"

COLORS = {"رمادي": (0.55, 0.55, 0.55), "أزرق": (0.28, 0.42, 0.85),
          "أحمر": (0.85, 0.25, 0.25), "أسود": (0.1, 0.1, 0.1)}


class StampTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.image_path = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(tr("stamp_title"))
        title.setObjectName("pageTitle")
        desc = QLabel(tr("stamp_desc"))
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            file_filter=PDF_FILTER, multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        # ===== علامة مائية =====
        wm_card = QFrame()
        wm_card.setObjectName("aboutCard")
        wm = QVBoxLayout(wm_card)
        wm.setContentsMargins(18, 14, 18, 14)
        wm.setSpacing(10)

        head = QLabel("💧  علامة مائية")
        head.setObjectName("cardTitle")
        wm.addWidget(head)

        self.wm_text = QLineEdit()
        self.wm_text.setPlaceholderText("نص العلامة المائية (يدعم العربية)")
        wm.addWidget(self.wm_text)

        opts1 = QHBoxLayout()
        opts1.addWidget(QLabel("الزاوية"))
        self.angle_combo = QComboBox()
        for a in (30, 45, 0, 90):
            self.angle_combo.addItem(f"{a}°", a)
        opts1.addWidget(self.angle_combo)

        opts1.addWidget(QLabel("الشفافية"))
        self.opacity_combo = QComboBox()
        for label, v in (("خفيفة جداً", 0.12), ("خفيفة", 0.22), ("متوسطة", 0.35), ("واضحة", 0.5)):
            self.opacity_combo.addItem(label, v)
        self.opacity_combo.setCurrentIndex(2)
        opts1.addWidget(self.opacity_combo)

        opts1.addWidget(QLabel("الحجم"))
        self.size_combo = QComboBox()
        for label, v in (("صغير", 28), ("متوسط", 48), ("كبير", 72)):
            self.size_combo.addItem(label, v)
        self.size_combo.setCurrentIndex(1)
        opts1.addWidget(self.size_combo)

        opts1.addWidget(QLabel("اللون"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(list(COLORS.keys()))
        opts1.addWidget(self.color_combo)
        opts1.addStretch()
        wm.addLayout(opts1)

        img_row = QHBoxLayout()
        self.use_image = QComboBox()
        self.use_image.addItem("نص فقط", "text")
        self.use_image.addItem("صورة كعلامة مائية", "image")
        self.img_pick = QPushButton("🖼️  اختر صورة…")
        self.img_pick.setObjectName("secondaryBtn")
        self.img_pick.clicked.connect(self._pick_image)
        self.img_label = QLabel("")
        self.img_label.setObjectName("hintLabel")
        img_row.addWidget(self.use_image)
        img_row.addWidget(self.img_pick)
        img_row.addWidget(self.img_label, 1)
        wm.addLayout(img_row)
        layout.addWidget(wm_card)

        # ===== ترقيم =====
        num_card = QFrame()
        num_card.setObjectName("aboutCard")
        nm = QVBoxLayout(num_card)
        nm.setContentsMargins(18, 14, 18, 14)
        nm.setSpacing(10)

        head2 = QLabel("🔢  ترقيم الصفحات")
        head2.setObjectName("cardTitle")
        nm.addWidget(head2)

        opts2 = QHBoxLayout()
        opts2.addWidget(QLabel("الصيغة"))
        self.num_mode = QComboBox()
        self.num_mode.addItem("صفحة 1 من 10", "page_of_ar")
        self.num_mode.addItem("Page 1 of 10", "page_of_en")
        self.num_mode.addItem("1", "x")
        self.num_mode.addItem("- 1 -", "dash")
        opts2.addWidget(self.num_mode)

        opts2.addWidget(QLabel("الموضع"))
        self.num_pos = QComboBox()
        self.num_pos.addItem("وسط أسفل", "bottom-center")
        self.num_pos.addItem("يسار أسفل", "bottom-left")
        self.num_pos.addItem("يمين أسفل", "bottom-right")
        self.num_pos.addItem("وسط أعلى", "top-center")
        opts2.addWidget(self.num_pos)
        opts2.addStretch()
        nm.addLayout(opts2)
        layout.addWidget(num_card)

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
        layout.addStretch()

        self.src_path = None

    def _on_file(self, paths):
        if not paths:
            return
        self.src_path = paths[0]
        self.status_label.setText(f"📄 {os.path.basename(self.src_path)}")
        self.run_btn.setEnabled(True)

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "اختر صورة العلامة المائية", "",
            "Images (*.png *.jpg *.jpeg *.webp)")
        if path:
            self.image_path = path
            self.img_label.setText(os.path.basename(path))

    def _run(self):
        if not self.src_path or self.worker:
            return
        use_image = self.use_image.currentData() == "image"
        text = self.wm_text.text().strip()
        if not use_image and not text and self.num_mode.currentData() in ("none",):
            show_toast(self, "أدخل نص العلامة المائية أو فعّل الترقيم", "warning")
            return
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("⏳ جارٍ التطبيق…")
        self.worker = Worker(self._do_work, use_image)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _do_work(self, use_image: bool):
        stem = os.path.splitext(self.src_path)[0]

        # 1) العلامة المائية (إن طُلبت)
        apply_wm = use_image and self.image_path or (not use_image and self.wm_text.text().strip())
        if apply_wm:
            tmp = stem + "_علامة_مؤقت.pdf"
            if use_image:
                watermark(self.src_path, tmp, image_path=self.image_path,
                          opacity=self.opacity_combo.currentData(),
                          angle=self.angle_combo.currentData())
            else:
                watermark(self.src_path, tmp, text=self.wm_text.text().strip(),
                          opacity=self.opacity_combo.currentData(),
                          angle=self.angle_combo.currentData(),
                          fontsize=self.size_combo.currentData(),
                          color=COLORS.get(self.color_combo.currentText()))
            src = tmp
        else:
            src = self.src_path

        # 2) الترقيم (دائماً — الصيغة الافتراضية مفيدة)
        out = stem + "_نهائي.pdf"
        add_page_numbers(src, out, mode=self.num_mode.currentData(),
                         position=self.num_pos.currentData())
        if src != self.src_path:
            try:
                os.unlink(tmp)
            except Exception:
                pass
        return {"out": out, "watermark": bool(apply_wm)}

    def _on_done(self, result):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        msg = "✅ تم التطبيق"
        if result["watermark"]:
            msg += " (علامة مائية + ترقيم)"
        else:
            msg += " (ترقيم)"
        show_toast(self, msg, "info")
        self.status_label.setText(f"✅ محفوظ: {result['out']}")
        record("علامة مائية وترقيم", result["out"])

    def _on_fail(self, err):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText(f"❌ {err}")
