import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QComboBox,
)

from ui.widgets import DropZone, Worker, CancellationToken
from ui.toast import show_toast
from core.ocr import ocr_pdf, tesseract_available


class OcrTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.worker = None
        self._build_ui()
        self._refresh_engine()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("التعرف الضوئي على الحروف (OCR)")
        title.setObjectName("pageTitle")
        desc = QLabel("حوّل المستندات الممسوحة إلى PDF قابل للبحث والنسخ — دعم العربية والإنجليزية")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.engine_label = QLabel("")
        self.engine_label.setObjectName("hintLabel")
        self.engine_label.setWordWrap(True)
        layout.addWidget(self.engine_label)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF ممسوحاً هنا أو انقر للاختيار",
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
        opts.addWidget(QLabel("اللغة:"))
        self.lang = QComboBox()
        self.lang.addItem("عربي + إنجليزي", "ara+eng")
        self.lang.addItem("عربي فقط", "ara")
        self.lang.addItem("إنجليزي فقط", "eng")
        opts.addWidget(self.lang)
        opts.addStretch()
        layout.addLayout(opts)

        run_row = QHBoxLayout()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.run_btn = QPushButton("بدء OCR")
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

    def _refresh_engine(self):
        ok, info = tesseract_available()
        if ok:
            self.engine_label.setText(f"محرك Tesseract جاهز: {info}")
        else:
            self.engine_label.setText(info)

    def _on_file(self, paths):
        if not paths or not paths[0].lower().endswith(".pdf"):
            show_toast(self, "اختر ملف PDF", "warning")
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
        ok, info = tesseract_available()
        if not ok:
            show_toast(self, "Tesseract غير متاح", "error")
            self.status_label.setText(info)
            return
        base = os.path.splitext(os.path.basename(self.selected_file))[0]
        output, _ = QFileDialog.getSaveFileName(
            self, "حفظ PDF القابل للبحث", f"{base}_OCR.pdf", "PDF Files (*.pdf)"
        )
        if not output:
            return

        token = CancellationToken()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.status_label.setText("جاري التعرف الضوئي… قد يستغرق وقتاً حسب عدد الصفحات")

        self.worker = Worker(
            ocr_pdf,
            self.selected_file,
            output,
            lang=self.lang.currentData(),
            cancel_token=token,
        )
        self.worker.finished_ok.connect(lambda res: self._done(True, res))
        self.worker.failed.connect(lambda e: self._done(False, e))
        self.worker.start()

    def _done(self, ok, payload):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if ok:
            msg = f"✅ تم إنشاء PDF قابل للبحث ({payload.get('pages')} صفحة)\n{payload.get('output')}"
            show_toast(self, "اكتمل OCR بنجاح", "success")
        else:
            msg = f"❌ {payload}"
            show_toast(self, str(payload), "error")
        self.status_label.setObjectName("statusSuccess" if ok else "statusError")
        self.status_label.setText(msg)
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
