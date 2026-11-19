import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QRadioButton, QButtonGroup,
)

from ui.widgets import DropZone, Worker, CancellationToken
from ui.toast import show_toast
from ui.i18n import tr_text, tr_fmt
from core.export import pdf_to_docx, pdf_to_excel


class ExportTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("تصدير إلى Word / Excel")
        title.setObjectName("pageTitle")
        desc = QLabel("استخرج النصوص إلى DOCX أو الجداول إلى XLSX مع الحفاظ على البنية قدر الإمكان")
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

        mode = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.word_radio = QRadioButton("Word (.docx)")
        self.word_radio.setChecked(True)
        self.excel_radio = QRadioButton("Excel (.xlsx)")
        self.mode_group.addButton(self.word_radio)
        self.mode_group.addButton(self.excel_radio)
        mode.addWidget(self.word_radio)
        mode.addWidget(self.excel_radio)
        mode.addStretch()
        layout.addLayout(mode)

        run_row = QHBoxLayout()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.run_btn = QPushButton("تصدير")
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
        base = os.path.splitext(os.path.basename(self.selected_file))[0]
        if self.word_radio.isChecked():
            output, _ = QFileDialog.getSaveFileName(
                self, tr_text("حفظ Word"), f"{base}.docx", "Word (*.docx)"
            )
            if not output:
                return
            fn = pdf_to_docx
            args = (self.selected_file, output)
            ok_msg = lambda res: tr_fmt("✅ تم التصدير إلى Word\n{res}", res=res)
        else:
            output, _ = QFileDialog.getSaveFileName(
                self, tr_text("حفظ Excel"), f"{base}.xlsx", "Excel (*.xlsx)"
            )
            if not output:
                return
            fn = pdf_to_excel
            args = (self.selected_file, output)
            ok_msg = lambda res: tr_fmt(
                "✅ تم التصدير إلى Excel — {tables} جدول\n{output}",
                tables=res.get("tables", 0), output=res.get("output"))

        token = CancellationToken()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.status_label.setText(tr_text("جاري التصدير…"))

        self.worker = Worker(fn, *args, cancel_token=token)
        self.worker.finished_ok.connect(lambda res: self._done(True, ok_msg(res)))
        self.worker.failed.connect(lambda e: self._done(False, e))
        self.worker.start()

    def _done(self, ok, msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setObjectName("statusSuccess" if ok else "statusError")
        self.status_label.setText(msg if ok else f"❌ {tr_text(msg)}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        show_toast(self, tr_text("تم التصدير") if ok else tr_text(str(msg)), "success" if ok else "error")
