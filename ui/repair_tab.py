"""تبويب إصلاح ملفات PDF التالفة."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
)

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr, tr_text, tr_fmt
from core.repair import repair, RepairError
from core.history import record
from core.compress import format_size

PDF_FILTER = "PDF (*.pdf)"


class RepairTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(tr("repair_title"))
        title.setObjectName("pageTitle")
        desc = QLabel(tr("repair_desc"))
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب الملف التالف هنا",
            sub_text="يعيد بناء بنية الملف: فهرس xref، الكائنات الناقصة، وترتيب الصفحات",
            file_filter=PDF_FILTER, multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("🩺  إصلاح الملف")
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
        try:
            size = os.path.getsize(self.src_path)
            self.status_label.setText(f"📄 {os.path.basename(self.src_path)} — {format_size(size)}")
        except OSError:
            self.status_label.setText(f"📄 {os.path.basename(self.src_path)}")
        self.run_btn.setEnabled(True)

    def _run(self):
        if not self.src_path or self.worker:
            return
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText(tr_text("⏳ جارٍ الإصلاح…"))
        out = os.path.splitext(self.src_path)[0] + tr_text("_مصلح.pdf")
        self.worker = Worker(repair, self.src_path, out)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _on_done(self, result):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        show_toast(self, tr_fmt("✅ أُصلح الملف عبر {engine}", engine=result['engine']), "info")
        self.status_label.setText(tr_fmt(
            "✅ محفوظ: {out} ({size} — المحرك: {engine})",
            out=result['out'], size=format_size(result['size']), engine=result['engine']))
        record("إصلاح PDF", result["out"])

    def _on_fail(self, err):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText(f"❌ {tr_text(err)}")
