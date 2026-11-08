import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QMessageBox, QProgressBar
)

from ui.widgets import DropZone, FileListWidget, Worker, make_toolbar_button
from core.merge import merge_pdfs, MergeError


class MergeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("دمج ملفات PDF")
        title.setObjectName("pageTitle")
        desc = QLabel("ادمج عدة ملفات PDF في ملف واحد — اسحب لإعادة ترتيب الملفات قبل الدمج")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملفات PDF هنا أو انقر للاختيار",
            sub_text="يمكن اختيار عدة ملفات (ملفين على الأقل)",
            file_filter="PDF Files (*.pdf)",
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
        self.run_btn = QPushButton("دمج الملفات")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run_merge)
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
        pdf_paths = [p for p in paths if p.lower().endswith(".pdf")]
        skipped = len(paths) - len(pdf_paths)
        if skipped:
            QMessageBox.information(self, "تنبيه", f"تم تجاهل {skipped} ملف غير PDF")
        self.file_list.add_files(pdf_paths)

    def _update_state(self):
        count = self.file_list.count()
        self.run_btn.setEnabled(count >= 2)
        self.status_label.setText("")

    def _run_merge(self):
        paths = self.file_list.get_paths()
        if len(paths) < 2:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ الملف المدموج", "ملف_مدموج.pdf", "PDF Files (*.pdf)"
        )
        if not output_path:
            return

        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("جاري الدمج...")

        self.worker = Worker(merge_pdfs, paths, output_path)
        self.worker.finished_ok.connect(lambda res: self._on_success(output_path, len(paths)))
        self.worker.failed.connect(self._on_failure)
        self.worker.start()

    def _on_success(self, output_path, count):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setObjectName("statusSuccess")
        self.status_label.setText(f"✅ تم دمج {count} ملفات بنجاح\nحُفظ في: {output_path}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)

    def _on_failure(self, error_msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setObjectName("statusError")
        self.status_label.setText(f"❌ فشلت العملية: {error_msg}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
