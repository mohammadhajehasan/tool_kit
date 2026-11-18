"""تبويب تحويل PDF إلى صور — صيغة/جودة/دقة قابلة للاختيار."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QProgressBar,
)

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr
from core.pdf2img import pdf_to_images, Pdf2ImgError
from core.history import record

PDF_FILTER = "PDF (*.pdf)"


class Pdf2ImgTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel(tr("pdf2img_title"))
        title.setObjectName("pageTitle")
        desc = QLabel(tr("pdf2img_desc"))
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            sub_text="ستُحفظ الصور في مجلد بجانب الملف",
            file_filter=PDF_FILTER, multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        opts = QHBoxLayout()
        opts.setSpacing(10)

        opts.addWidget(QLabel("الصيغة"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["JPG", "PNG"])
        opts.addWidget(self.fmt_combo)

        opts.addWidget(QLabel("الجودة"))
        self.q_combo = QComboBox()
        self.q_combo.addItem("عالية (92)", 92)
        self.q_combo.addItem("متوازنة (80)", 80)
        self.q_combo.addItem("ملف صغير (60)", 60)
        self.q_combo.setCurrentIndex(1)
        opts.addWidget(self.q_combo)

        opts.addWidget(QLabel("الدقة"))
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItem("شاشة (144)", 144)
        self.dpi_combo.addItem("عالية (200)", 200)
        self.dpi_combo.addItem("طباعة (300)", 300)
        self.dpi_combo.setCurrentIndex(1)
        opts.addWidget(self.dpi_combo)

        opts.addWidget(QLabel("الصفحات"))
        self.pages_edit = QLineEdit()
        self.pages_edit.setPlaceholderText("مثال: 1-3,5 (فارغ = كل الصفحات)")
        self.pages_edit.setMaximumWidth(200)
        opts.addWidget(self.pages_edit, 1)
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

        self.open_btn = QPushButton(tr("open_folder"))
        self.open_btn.setObjectName("secondaryBtn")
        self.open_btn.setVisible(False)
        self.open_btn.clicked.connect(self._open_folder)
        layout.addWidget(self.open_btn)

        layout.addStretch()
        self.src_path = None
        self.out_dir = None

    def _on_file(self, paths):
        if not paths:
            return
        self.src_path = paths[0]
        self.status_label.setText(f"📄 {os.path.basename(self.src_path)}")
        self.run_btn.setEnabled(True)
        self.open_btn.setVisible(False)

    def _parse_pages(self, total: int):
        text = self.pages_edit.text().strip()
        if not text:
            return None
        from core.split import parse_page_ranges
        return parse_page_ranges(text, total)

    def _run(self):
        if not self.src_path or self.worker:
            return
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("⏳ جارٍ التحويل…")
        self.worker = Worker(self._do_convert)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _do_convert(self):
        import fitz
        doc = fitz.open(self.src_path)
        total = len(doc)
        doc.close()
        pages = self._parse_pages(total)
        fmt = self.fmt_combo.currentText().lower()
        out_dir = os.path.splitext(self.src_path)[0] + "_صور"
        return pdf_to_images(
            self.src_path, out_dir, fmt=fmt,
            dpi=self.dpi_combo.currentData(),
            quality=self.q_combo.currentData(),
            pages=pages,
        )

    def _on_done(self, files):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.out_dir = os.path.dirname(files[0]) if files else None
        show_toast(self, f"✅ تم تحويل {len(files)} صفحة إلى صور", "info")
        self.status_label.setText(f"✅ {len(files)} صورة في: {self.out_dir}")
        self.open_btn.setVisible(True)
        record("PDF إلى صور", self.out_dir or self.src_path)

    def _on_fail(self, err):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText(f"❌ {err}")

    def _open_folder(self):
        if self.out_dir and os.path.isdir(self.out_dir):
            os.startfile(self.out_dir)
