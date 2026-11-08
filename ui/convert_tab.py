import os
import tempfile
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QMessageBox, QProgressBar
)

from ui.widgets import DropZone, FileListWidget, Worker, make_toolbar_button
from core.convert import images_to_pdf, is_supported_image, ConvertError, SUPPORTED_EXTENSIONS


IMAGE_FILTER = "Images (*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp *.gif)"


class ConvertTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("تحويل الصور إلى PDF")
        title.setObjectName("pageTitle")
        desc = QLabel("حوّل صورة واحدة أو عدة صور (JPG, PNG, BMP, WEBP...) إلى ملف PDF واحد")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب الصور هنا أو انقر للاختيار",
            sub_text="يمكن اختيار عدة صور بترتيب معيّن",
            file_filter=IMAGE_FILTER,
            multiple=True,
        )
        self.drop_zone.filesDropped.connect(self._on_files_added)
        layout.addWidget(self.drop_zone)

        self.file_list = FileListWidget()
        self.file_list.setMinimumHeight(180)
        self.file_list.filesChanged.connect(self._update_state)
        layout.addWidget(self.file_list)

        toolbar = QHBoxLayout()
        self.remove_btn = make_toolbar_button("حذف المحدد", danger=True)
        self.remove_btn.clicked.connect(self.file_list.remove_selected)
        self.clear_btn = make_toolbar_button("مسح الكل", danger=True)
        self.clear_btn.clicked.connect(self.file_list.clear_all)
        toolbar.addWidget(self.remove_btn)
        toolbar.addWidget(self.clear_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("تحويل إلى PDF")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run_convert)
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

    def _on_files_added(self, paths):
        valid_paths = [p for p in paths if is_supported_image(p)]
        skipped = len(paths) - len(valid_paths)
        if skipped:
            QMessageBox.information(self, "تنبيه", f"تم تجاهل {skipped} ملف بصيغة غير مدعومة")
        self.file_list.add_files(valid_paths)

    def _update_state(self):
        self.run_btn.setEnabled(self.file_list.count() >= 1)
        self.status_label.setText("")

    def _run_convert(self):
        paths = self.file_list.get_paths()
        if not paths:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ ملف PDF", "صور_محولة.pdf", "PDF Files (*.pdf)"
        )
        if not output_path:
            return

        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("جاري التحويل...")

        tmp_dir = os.path.join(tempfile.gettempdir(), "pdf_toolbox_tmp")
        self.worker = Worker(images_to_pdf, paths, output_path, tmp_dir)
        self.worker.finished_ok.connect(lambda res: self._on_success(output_path, len(paths)))
        self.worker.failed.connect(self._on_failure)
        self.worker.start()

    def _on_success(self, output_path, count):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setObjectName("statusSuccess")
        self.status_label.setText(f"✅ تم تحويل {count} صورة إلى PDF بنجاح\nحُفظ في: {output_path}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)

    def _on_failure(self, error_msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setObjectName("statusError")
        self.status_label.setText(f"❌ فشلت العملية: {error_msg}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
