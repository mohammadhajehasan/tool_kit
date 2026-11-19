"""تبويب استخراج النصوص والصور من PDF."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QProgressBar, QRadioButton, QButtonGroup, QFrame,
)
from PySide6.QtCore import Qt

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr, tr_text, tr_fmt
from core.extract import extract_text, extract_images, ExtractError
from core.history import record

PDF_FILTER = "PDF (*.pdf)"


class ExtractTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel(tr("extract_title"))
        title.setObjectName("pageTitle")
        desc = QLabel(tr("extract_desc"))
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            file_filter=PDF_FILTER, multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        mode_row = QHBoxLayout()
        self.group = QButtonGroup(self)
        for value, label in (("text", "📃  استخراج النص إلى ملف txt"),
                             ("images", "🖼️  استخراج الصور المضمّنة")):
            rb = QRadioButton(label)
            rb.setChecked(value == "text")
            self.group.addButton(rb)
            self.group.idClicked.connect(lambda *_: None)
            rb.setProperty("value", value)
            mode_row.addWidget(rb)
        self.group.buttons()[0].setChecked(True)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        pages_row = QHBoxLayout()
        pages_row.addWidget(QLabel("الصفحات"))
        self.pages_edit = QLineEdit()
        self.pages_edit.setPlaceholderText("مثال: 1-3,5 (فارغ = كل الصفحات)")
        self.pages_edit.setMaximumWidth(220)
        pages_row.addWidget(self.pages_edit)
        pages_row.addStretch()
        layout.addLayout(pages_row)

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
        self.out_path = None

    def _on_file(self, paths):
        if not paths:
            return
        self.src_path = paths[0]
        self.status_label.setText(f"📄 {os.path.basename(self.src_path)}")
        self.run_btn.setEnabled(True)
        self.open_btn.setVisible(False)

    def _selected_mode(self) -> str:
        for rb in self.group.buttons():
            if rb.isChecked():
                return rb.property("value")
        return "text"

    def _run(self):
        if not self.src_path or self.worker:
            return
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText(tr_text("⏳ جارٍ الاستخراج…"))
        self.worker = Worker(self._do_extract)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _do_extract(self):
        import fitz
        from core.split import parse_page_ranges
        doc = fitz.open(self.src_path)
        total = len(doc)
        doc.close()
        pages = None
        if self.pages_edit.text().strip():
            pages = parse_page_ranges(self.pages_edit.text().strip(), total)

        mode = self._selected_mode()
        stem = os.path.splitext(self.src_path)[0]
        if mode == "text":
            out = stem + ".txt"
            return {"mode": "text", **extract_text(self.src_path, out, pages)}
        out_dir = stem + tr_text("_صور")
        return {"mode": "images", **extract_images(self.src_path, out_dir)}

    def _on_done(self, result):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        if result["mode"] == "text":
            self.out_path = result["out"]
            show_toast(self, tr_fmt("✅ استُخرج النص ({chars} حرفاً)", chars=result["chars"]), "info")
            self.status_label.setText(tr_fmt("✅ النص محفوظ في: {out}", out=result["out"]))
            record("استخراج نص", result["out"])
        else:
            self.out_path = result["dir"]
            show_toast(self, tr_fmt("✅ استُخرجت {count} صورة", count=result["count"]), "info")
            self.status_label.setText(tr_fmt("✅ {count} صورة في: {dir}", count=result["count"], dir=result["dir"]))
            record("استخراج صور", result["dir"])
        self.open_btn.setVisible(True)

    def _on_fail(self, err):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText(f"❌ {tr_text(err)}")

    def _open_folder(self):
        if not self.out_path:
            return
        target = self.out_path if os.path.isdir(self.out_path) else os.path.dirname(self.out_path)
        if os.path.isdir(target):
            os.startfile(target)
