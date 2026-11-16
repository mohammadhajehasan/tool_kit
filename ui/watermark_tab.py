import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QDoubleSpinBox, QSpinBox, QRadioButton, QButtonGroup,
)

from ui.widgets import DropZone, Worker, CancellationToken
from ui.toast import show_toast
from core.watermark import add_text_watermark, add_image_watermark


class WatermarkTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.image_path = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("العلامة المائية")
        title.setObjectName("pageTitle")
        desc = QLabel("أضف نصاً أو شعاراً شفافاً على صفحات المستند مع التحكم بالميلان والحجم")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            sub_text="ملف واحد",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
            min_height=140,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        self.file_label = QLabel("")
        self.file_label.setObjectName("fileMeta")
        layout.addWidget(self.file_label)

        mode = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.text_radio = QRadioButton("نص")
        self.text_radio.setChecked(True)
        self.img_radio = QRadioButton("صورة / شعار")
        self.mode_group.addButton(self.text_radio)
        self.mode_group.addButton(self.img_radio)
        mode.addWidget(self.text_radio)
        mode.addWidget(self.img_radio)
        mode.addStretch()
        layout.addLayout(mode)

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("مثال: سري للغاية — مسودة — خاص")
        layout.addWidget(self.text_edit)

        img_row = QHBoxLayout()
        self.img_btn = QPushButton("اختيار صورة العلامة…")
        self.img_btn.clicked.connect(self._pick_image)
        self.img_label = QLabel("لم تُختر صورة")
        self.img_label.setObjectName("hintLabel")
        img_row.addWidget(self.img_btn)
        img_row.addWidget(self.img_label, 1)
        layout.addLayout(img_row)

        opts = QHBoxLayout()
        opts.addWidget(QLabel("الشفافية:"))
        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.05, 1.0)
        self.opacity.setSingleStep(0.05)
        self.opacity.setValue(0.25)
        opts.addWidget(self.opacity)
        opts.addWidget(QLabel("الزاوية:"))
        self.angle = QDoubleSpinBox()
        self.angle.setRange(-90, 90)
        self.angle.setValue(45)
        opts.addWidget(self.angle)
        opts.addWidget(QLabel("حجم الخط:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(12, 120)
        self.font_size.setValue(48)
        opts.addWidget(self.font_size)
        opts.addStretch()
        layout.addLayout(opts)

        self.text_radio.toggled.connect(self._sync)
        self._sync()

        run_row = QHBoxLayout()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.run_btn = QPushButton("تطبيق العلامة")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        run_row.addStretch()
        run_row.addWidget(self.cancel_btn)
        run_row.addWidget(self.run_btn)
        layout.addLayout(run_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _sync(self):
        is_text = self.text_radio.isChecked()
        self.text_edit.setVisible(is_text)
        self.angle.setEnabled(is_text)
        self.font_size.setEnabled(is_text)
        self.img_btn.setVisible(not is_text)
        self.img_label.setVisible(not is_text)

    def _on_file(self, paths):
        if not paths or not paths[0].lower().endswith(".pdf"):
            show_toast(self, "الرجاء اختيار ملف PDF", "warning")
            return
        self.selected_file = paths[0]
        self.file_label.setText(f"📄 {os.path.basename(paths[0])}")
        self.run_btn.setEnabled(True)

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "صورة العلامة", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.image_path = path
            self.img_label.setText(os.path.basename(path))

    def _cancel(self):
        if self.worker:
            self.worker.cancel()

    def _run(self):
        if not self.selected_file:
            return
        base = os.path.splitext(os.path.basename(self.selected_file))[0]
        output, _ = QFileDialog.getSaveFileName(
            self, "حفظ الملف", f"{base}_علامة.pdf", "PDF Files (*.pdf)"
        )
        if not output:
            return

        token = CancellationToken()
        if self.text_radio.isChecked():
            text = self.text_edit.text().strip()
            if not text:
                show_toast(self, "أدخل نص العلامة المائية", "warning")
                return
            fn = add_text_watermark
            kwargs = dict(
                input_path=self.selected_file,
                output_path=output,
                text=text,
                opacity=self.opacity.value(),
                angle=self.angle.value(),
                font_size=float(self.font_size.value()),
            )
        else:
            if not self.image_path:
                show_toast(self, "اختر صورة العلامة أولاً", "warning")
                return
            fn = add_image_watermark
            kwargs = dict(
                input_path=self.selected_file,
                output_path=output,
                image_path=self.image_path,
                opacity=self.opacity.value(),
            )

        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.status_label.setText("جاري التطبيق...")

        self.worker = Worker(fn, cancel_token=token, **kwargs)
        self.worker.finished_ok.connect(lambda _: self._done(True, output))
        self.worker.failed.connect(lambda e: self._done(False, e))
        self.worker.start()

    def _done(self, ok, payload):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if ok:
            msg = f"✅ تمت إضافة العلامة المائية\n{payload}"
            show_toast(self, "تمت إضافة العلامة المائية", "success")
        else:
            msg = f"❌ {payload}"
            show_toast(self, str(payload), "error")
        self.status_label.setObjectName("statusSuccess" if ok else "statusError")
        self.status_label.setText(msg)
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
