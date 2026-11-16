import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QCheckBox, QRadioButton, QButtonGroup,
)
from PySide6.QtCore import Qt

from ui.widgets import DropZone, Worker, CancellationToken
from ui.toast import show_toast
from core.protect import protect_pdf, unlock_pdf, ProtectError


class ProtectTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.worker = None
        self._token = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("حماية وتشفير PDF")
        title.setObjectName("pageTitle")
        desc = QLabel("شفّر الملف بكلمة مرور (AES-256) أو ألغِ الحماية بعد إدخال كلمة السر")
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

        mode_row = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.protect_radio = QRadioButton("تشفير وحماية")
        self.protect_radio.setChecked(True)
        self.unlock_radio = QRadioButton("إلغاء الحماية")
        self.mode_group.addButton(self.protect_radio)
        self.mode_group.addButton(self.unlock_radio)
        mode_row.addWidget(self.protect_radio)
        mode_row.addWidget(self.unlock_radio)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setPlaceholderText("كلمة المرور")
        layout.addWidget(self.pass_edit)

        self.owner_edit = QLineEdit()
        self.owner_edit.setEchoMode(QLineEdit.Password)
        self.owner_edit.setPlaceholderText("كلمة مرور المالك (اختياري — للصلاحيات)")
        layout.addWidget(self.owner_edit)

        perms = QHBoxLayout()
        self.allow_print = QCheckBox("السماح بالطباعة")
        self.allow_print.setChecked(True)
        self.allow_copy = QCheckBox("السماح بالنسخ")
        self.allow_modify = QCheckBox("السماح بالتعديل")
        perms.addWidget(self.allow_print)
        perms.addWidget(self.allow_copy)
        perms.addWidget(self.allow_modify)
        perms.addStretch()
        layout.addLayout(perms)

        self.protect_radio.toggled.connect(self._sync_mode)
        self._sync_mode()

        run_row = QHBoxLayout()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.run_btn = QPushButton("تنفيذ")
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

    def _sync_mode(self):
        protecting = self.protect_radio.isChecked()
        self.owner_edit.setVisible(protecting)
        self.allow_print.setVisible(protecting)
        self.allow_copy.setVisible(protecting)
        self.allow_modify.setVisible(protecting)

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
        password = self.pass_edit.text()
        if not password:
            show_toast(self, "أدخل كلمة المرور", "warning")
            return

        base = os.path.splitext(os.path.basename(self.selected_file))[0]
        if self.protect_radio.isChecked():
            suggested = f"{base}_محمي.pdf"
            output, _ = QFileDialog.getSaveFileName(self, "حفظ الملف المحمي", suggested, "PDF Files (*.pdf)")
            if not output:
                return
            fn = protect_pdf
            kwargs = dict(
                input_path=self.selected_file,
                output_path=output,
                user_password=password,
                owner_password=self.owner_edit.text() or None,
                allow_print=self.allow_print.isChecked(),
                allow_copy=self.allow_copy.isChecked(),
                allow_modify=self.allow_modify.isChecked(),
            )
            ok_msg = f"تم تشفير الملف بنجاح\n{output}"
        else:
            suggested = f"{base}_بدون_حماية.pdf"
            output, _ = QFileDialog.getSaveFileName(self, "حفظ الملف", suggested, "PDF Files (*.pdf)")
            if not output:
                return
            fn = unlock_pdf
            kwargs = dict(input_path=self.selected_file, output_path=output, password=password)
            ok_msg = f"تم إلغاء الحماية بنجاح\n{output}"

        self._token = CancellationToken()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.status_label.setText("جاري المعالجة...")

        self.worker = Worker(fn, cancel_token=self._token, **kwargs)
        self.worker.finished_ok.connect(lambda _: self._done(True, ok_msg))
        self.worker.failed.connect(lambda e: self._done(False, e))
        self.worker.start()

    def _done(self, ok, msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setObjectName("statusSuccess" if ok else "statusError")
        self.status_label.setText(("✅ " if ok else "❌ ") + str(msg))
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        show_toast(self, "تمت العملية بنجاح" if ok else f"فشل: {msg}", "success" if ok else "error")
