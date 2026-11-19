"""تبويب حماية PDF — تشفير AES-256 أو إزالة التشفير."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QCheckBox, QRadioButton, QButtonGroup, QProgressBar,
)

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr, tr_text, tr_fmt
from core.protect import protect, unprotect, is_encrypted, ProtectError
from core.history import record

PDF_FILTER = "PDF (*.pdf)"


class ProtectTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(tr("protect_title"))
        title.setObjectName("pageTitle")
        desc = QLabel(tr("protect_desc"))
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            file_filter=PDF_FILTER, multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        # --- الوضع ---
        mode_row = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.encrypt_rb = QRadioButton("🔒  تشفير بحماية")
        self.decrypt_rb = QRadioButton("🔓  إزالة الحماية")
        self.encrypt_rb.setChecked(True)
        self.mode_group.addButton(self.encrypt_rb)
        self.mode_group.addButton(self.decrypt_rb)
        self.encrypt_rb.toggled.connect(self._mode_changed)
        mode_row.addWidget(self.encrypt_rb)
        mode_row.addWidget(self.decrypt_rb)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        # --- كلمات المرور ---
        pw_row = QHBoxLayout()
        self.pw1 = QLineEdit()
        self.pw1.setEchoMode(QLineEdit.Password)
        self.pw1.setPlaceholderText("كلمة المرور")
        self.pw2 = QLineEdit()
        self.pw2.setEchoMode(QLineEdit.Password)
        self.pw2.setPlaceholderText("تأكيد كلمة المرور")
        pw_row.addWidget(self.pw1, 1)
        pw_row.addWidget(self.pw2, 1)
        layout.addLayout(pw_row)

        # --- الأذونات (تشفير فقط) ---
        perms_row = QHBoxLayout()
        self.allow_print = QCheckBox("السماح بالطباعة")
        self.allow_print.setChecked(True)
        self.allow_copy = QCheckBox("السماح بنسخ النص")
        self.allow_modify = QCheckBox("السماح بالتعديل")
        for w in (self.allow_print, self.allow_copy, self.allow_modify):
            perms_row.addWidget(w)
        perms_row.addStretch()
        layout.addLayout(perms_row)

        self.hint = QLabel("AES-256 — لا يمكن استعادة الملف إن نسيت كلمة المرور")
        self.hint.setObjectName("hintLabel")
        layout.addWidget(self.hint)

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
        layout.addStretch()

        self.src_path = None

    def _on_file(self, paths):
        if not paths:
            return
        self.src_path = paths[0]
        encrypted = False
        try:
            encrypted = is_encrypted(self.src_path)
        except Exception:
            pass
        if encrypted:
            self.decrypt_rb.setChecked(True)
        name = os.path.basename(self.src_path)
        if encrypted:
            self.status_label.setText(
                tr_fmt("📄 {name} — 🔒 محمي (سيُفعّل وضع فك الحماية)", name=name))
        else:
            self.status_label.setText(f"📄 {name}")
        self.run_btn.setEnabled(True)

    def _mode_changed(self):
        enc = self.encrypt_rb.isChecked()
        self.pw2.setVisible(enc)
        for w in (self.allow_print, self.allow_copy, self.allow_modify, self.hint):
            w.setVisible(enc)

    def _run(self):
        if not self.src_path or self.worker:
            return
        if self.encrypt_rb.isChecked():
            pw = self.pw1.text()
            if not pw:
                show_toast(self, "أدخل كلمة المرور أولاً", "warning")
                return
            if pw != self.pw2.text():
                show_toast(self, "كلمتا المرور غير متطابقتين", "warning")
                return
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText(tr_text("⏳ جارٍ التنفيذ…"))
        self.worker = Worker(self._do_work)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _do_work(self):
        stem = os.path.splitext(self.src_path)[0]
        if self.encrypt_rb.isChecked():
            out = stem + tr_text("_محمي.pdf")
            protect(
                self.src_path, out,
                user_password=self.pw1.text(),
                allow_print=self.allow_print.isChecked(),
                allow_copy=self.allow_copy.isChecked(),
                allow_modify=self.allow_modify.isChecked(),
            )
            return {"mode": "encrypt", "out": out}
        out = stem + tr_text("_بدون_حماية.pdf")
        unprotect(self.src_path, out, self.pw1.text())
        return {"mode": "decrypt", "out": out}

    def _on_done(self, result):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        label = tr_text("حُمي") if result["mode"] == "encrypt" else tr_text("أُزيلت حمايته")
        show_toast(self, tr_fmt("✅ {label} الملف بنجاح", label=label), "info")
        self.status_label.setText(f"✅ {label}: {result['out']}")
        record("حماية PDF", result["out"])

    def _on_fail(self, err):
        self.worker = None
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText(f"❌ {tr_text(err)}")
