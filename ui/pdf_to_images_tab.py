import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QSpinBox, QComboBox,
)

from ui.widgets import DropZone, Worker, CancellationToken
from ui.toast import show_toast
from core.pdf_to_images import pdf_to_images


class PdfToImagesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("تحويل PDF إلى صور")
        title.setObjectName("pageTitle")
        desc = QLabel("صدّر صفحات المستند كصور PNG أو JPG بدقة قابلة للتخصيص")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            sub_text="ملف واحد",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        self.file_label = QLabel("")
        self.file_label.setObjectName("fileMeta")
        layout.addWidget(self.file_label)

        opts = QHBoxLayout()
        opts.addWidget(QLabel("الدقة (DPI):"))
        self.dpi = QSpinBox()
        self.dpi.setRange(72, 600)
        self.dpi.setValue(150)
        opts.addWidget(self.dpi)
        opts.addWidget(QLabel("الصيغة:"))
        self.fmt = QComboBox()
        self.fmt.addItems(["PNG", "JPG"])
        opts.addWidget(self.fmt)
        opts.addStretch()
        layout.addLayout(opts)

        run_row = QHBoxLayout()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.run_btn = QPushButton("تصدير الصور")
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

    def _on_file(self, paths):
        if not paths or not paths[0].lower().endswith(".pdf"):
            show_toast(self, "الرجاء اختيار ملف PDF", "warning")
            return
        self.selected_file = paths[0]
        self.file_label.setText(f"📄 {os.path.basename(paths[0])}")
        self.run_btn.setEnabled(True)

    def _cancel(self):
        if self.worker:
            self.worker.cancel()

    def _run(self):
        if not self.selected_file:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "اختر مجلد حفظ الصور")
        if not out_dir:
            return

        token = CancellationToken()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.status_label.setText("جاري التصدير...")

        self.worker = Worker(
            pdf_to_images,
            self.selected_file,
            out_dir,
            dpi=self.dpi.value(),
            fmt=self.fmt.currentText().lower(),
            cancel_token=token,
        )
        self.worker.finished_ok.connect(lambda res: self._done(True, res, out_dir))
        self.worker.failed.connect(lambda e: self._done(False, e, out_dir))
        self.worker.start()

    def _done(self, ok, payload, out_dir):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if ok:
            msg = f"✅ تم تصدير {len(payload)} صورة\nالمجلد: {out_dir}"
            show_toast(self, f"تم تصدير {len(payload)} صورة", "success")
        else:
            msg = f"❌ {payload}"
            show_toast(self, str(payload), "error")
        self.status_label.setObjectName("statusSuccess" if ok else "statusError")
        self.status_label.setText(msg)
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
