import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QTextBrowser,
)

from ui.widgets import DropZone, Worker, CancellationToken
from ui.toast import show_toast
from ui import i18n
from ui.i18n import tr_text, tr_fmt
from core.pdf_diff import compare_pdfs


class DiffTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_a = None
        self.file_b = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("مقارنة ملفات PDF")
        title.setObjectName("pageTitle")
        desc = QLabel("ارفع نسختين لعرض الفروقات: أحمر للحذف وأخضر للإضافة")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        zones = QHBoxLayout()
        self.drop_a = DropZone(
            hint_text="الملف الأصلي (أ)",
            sub_text="PDF",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
            min_height=120,
        )
        self.drop_b = DropZone(
            hint_text="الملف الجديد (ب)",
            sub_text="PDF",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
            min_height=120,
        )
        self.drop_a.filesDropped.connect(lambda p: self._set_file("a", p))
        self.drop_b.filesDropped.connect(lambda p: self._set_file("b", p))
        zones.addWidget(self.drop_a)
        zones.addWidget(self.drop_b)
        layout.addLayout(zones)

        self.meta = QLabel("")
        self.meta.setObjectName("fileMeta")
        self.meta.setWordWrap(True)
        layout.addWidget(self.meta)

        run_row = QHBoxLayout()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.run_btn = QPushButton("قارن الآن")
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

        self.summary = QLabel("")
        self.summary.setObjectName("accentLabel")
        layout.addWidget(self.summary)

        self.viewer = QTextBrowser()
        self.viewer.setMinimumHeight(280)
        self.viewer.setOpenExternalLinks(False)
        layout.addWidget(self.viewer, 1)

    def _set_file(self, which, paths):
        if not paths or not paths[0].lower().endswith(".pdf"):
            show_toast(self, "اختر ملف PDF", "warning")
            return
        if which == "a":
            self.file_a = paths[0]
        else:
            self.file_b = paths[0]
        a = os.path.basename(self.file_a) if self.file_a else "—"
        b = os.path.basename(self.file_b) if self.file_b else "—"
        self.meta.setText(tr_fmt("أ: {a}\nب: {b}", a=a, b=b))
        self.run_btn.setEnabled(bool(self.file_a and self.file_b))

    def _cancel(self):
        if self.worker:
            self.worker.cancel()

    def _run(self):
        if not (self.file_a and self.file_b):
            return
        token = CancellationToken()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.summary.setText(tr_text("جاري المقارنة…"))

        self.worker = Worker(compare_pdfs, self.file_a, self.file_b, cancel_token=token)
        self.worker.finished_ok.connect(self._ok)
        self.worker.failed.connect(self._fail)
        self.worker.start()

    def _ok(self, result):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.summary.setText(tr_fmt(
            "صفحات أ={a} | ب={b} — إضافات: {added} | حذف: {removed}",
            a=result.pages_a, b=result.pages_b,
            added=result.added, removed=result.removed))
        html = result.html
        if not i18n.rtl():
            html = html.replace("direction:rtl", "direction:ltr", 1)
            html = html.replace("نتيجة المقارنة", "Comparison result")
            import re
            html = re.sub(r"—+ صفحة (\d+) —+", r"—— Page \1 ——", html)
        self.viewer.setHtml(html)
        show_toast(self, tr_text("اكتملت المقارنة"), "success")

    def _fail(self, err):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.summary.setText(f"❌ {tr_text(err)}")
        show_toast(self, err, "error")
