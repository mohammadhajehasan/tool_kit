import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QProgressBar, QRadioButton, QButtonGroup, QComboBox,
    QCheckBox,
)

from ui.widgets import DropZone, Worker, CancellationToken
from ui.toast import show_toast
from ui import i18n
from ui.i18n import tr_text, tr_fmt
from core.ai_assistant import (
    ask_about_document, summarize_document,
    ollama_available, list_ollama_models,
)
from core import unlimited_ocr as U


class AiTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.worker = None
        self._build_ui()
        self._refresh_ollama()

    def _settings_path(self):
        from core import app_settings
        return app_settings.SETTINGS_PATH

    def _load_api_key(self) -> str:
        try:
            from core import app_settings
            return app_settings.load().get("ai_api_key", "")
        except Exception:
            return ""

    def _save_api_key(self, key: str):
        try:
            from core import app_settings
            app_settings.save({"ai_api_key": key})
        except Exception:
            pass

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("المساعد الذكي للمستندات")
        title.setObjectName("pageTitle")
        desc = QLabel("تلخيص وأسئلة حول محتوى الملف — محلياً عبر Ollama أو بمفتاح API اختياري")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا",
            sub_text="يُفضّل مستنداً فيه طبقة نص (أو بعد OCR)",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
            min_height=120,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        self.file_label = QLabel("")
        self.file_label.setObjectName("fileMeta")
        layout.addWidget(self.file_label)

        mode = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.ollama_radio = QRadioButton("Ollama محلي")
        self.ollama_radio.setChecked(True)
        self.api_radio = QRadioButton("API سحابي")
        self.mode_group.addButton(self.ollama_radio)
        self.mode_group.addButton(self.api_radio)
        mode.addWidget(self.ollama_radio)
        mode.addWidget(self.api_radio)
        mode.addStretch()
        layout.addLayout(mode)

        self.status_engine = QLabel("")
        self.status_engine.setObjectName("hintLabel")
        self.status_engine.setWordWrap(True)
        layout.addWidget(self.status_engine)

        self.ocr_check = QCheckBox("استخدم Unlimited-OCR للمستندات الممسوحة تلقائياً")
        self.ocr_check.setToolTip("يتطلب ضبط خادم Unlimited-OCR في تبويب OCR")
        self.ocr_check.setChecked(bool(U.load_config().get("unlimited_ocr_ai_ocr", True)))
        self.ocr_check.toggled.connect(self._save_ocr_pref)
        layout.addWidget(self.ocr_check)

        self.ocr_hint = QLabel("")
        self.ocr_hint.setObjectName("hintLabel")
        self.ocr_hint.setWordWrap(True)
        layout.addWidget(self.ocr_hint)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("النموذج:"))
        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.addItems(["llama3.2", "llama3.1", "mistral", "qwen2.5", "gpt-4o-mini"])
        model_row.addWidget(self.model, 1)
        layout.addLayout(model_row)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("مفتاح API (اختياري — يُحفظ محلياً)")
        self.api_key.setText(self._load_api_key())
        layout.addWidget(self.api_key)

        self.question = QLineEdit()
        self.question.setPlaceholderText("اسأل عن المستند… مثال: ما أهم بنود العقد؟")
        layout.addWidget(self.question)

        btns = QHBoxLayout()
        self.summarize_btn = QPushButton("تلخيص")
        self.summarize_btn.setEnabled(False)
        self.summarize_btn.clicked.connect(self._summarize)
        self.ask_btn = QPushButton("اسأل")
        self.ask_btn.setObjectName("primaryBtn")
        self.ask_btn.setEnabled(False)
        self.ask_btn.clicked.connect(self._ask)
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        btns.addWidget(self.summarize_btn)
        btns.addStretch()
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.ask_btn)
        layout.addLayout(btns)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.answer = QTextEdit()
        self.answer.setReadOnly(True)
        self.answer.setMinimumHeight(220)
        self.answer.setPlaceholderText("ستظهر الإجابة هنا…")
        layout.addWidget(self.answer, 1)

        self.ollama_radio.toggled.connect(self._refresh_ollama)

    def _refresh_ollama(self):
        self._refresh_ocr_hint()
        if self.ollama_radio.isChecked():
            if ollama_available():
                models = list_ollama_models()
                text = tr_text("Ollama متصل محلياً")
                if models:
                    text += tr_fmt(" — نماذج: {models}", models=", ".join(models[:6]))
                self.status_engine.setText(text)
                if models:
                    self.model.clear()
                    self.model.addItems(models)
            else:
                self.status_engine.setText(
                    tr_text("Ollama غير متصل. ثبّته من ollama.com ثم: ollama run llama3.2")
                )
        else:
            self.status_engine.setText(
                tr_text("وضع API: يُرسل النص إلى مزود متوافق مع OpenAI (اختياري)"))

    def _on_file(self, paths):
        if not paths or not paths[0].lower().endswith(".pdf"):
            show_toast(self, "اختر ملف PDF", "warning")
            return
        self.selected_file = paths[0]
        self.file_label.setText(f"📄 {os.path.basename(paths[0])}")
        self.ask_btn.setEnabled(True)
        self.summarize_btn.setEnabled(True)

    def _cancel(self):
        if self.worker:
            self.worker.cancel()

    def _save_ocr_pref(self, checked: bool):
        try:
            U.save_config({"unlimited_ocr_ai_ocr": bool(checked)})
        except Exception:
            pass
        self._refresh_ocr_hint()

    def _refresh_ocr_hint(self):
        if not hasattr(self, "ocr_hint"):
            return
        cfg = U.load_config()
        if self.ocr_check.isChecked() and not U.is_configured(cfg):
            self.ocr_hint.setText(tr_text(
                "⚠️ اضبط خادم Unlimited-OCR في تبويب OCR أولاً"))
        else:
            self.ocr_hint.setText("")

    def _mode_kwargs(self):
        mode = "api" if self.api_radio.isChecked() else "ollama"
        key = self.api_key.text().strip()
        if mode == "api" and key:
            self._save_api_key(key)
        return dict(
            mode=mode,
            model=self.model.currentText().strip() or "llama3.2",
            api_key=key,
            lang=i18n.lang(),
            ocr_fallback=self.ocr_check.isChecked(),
            ocr_config=U.load_config(),
        )

    def _start(self, fn, *args):
        token = CancellationToken()
        self.ask_btn.setEnabled(False)
        self.summarize_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.answer.setPlainText(tr_text("جاري التفكير…"))
        self.worker = Worker(fn, *args, cancel_token=token, **self._mode_kwargs())
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._ok)
        self.worker.failed.connect(self._fail)
        self.worker.start()

    def _on_progress(self, message: str):
        self.answer.setPlainText(tr_text(str(message)))

    def _ask(self):
        if not self.selected_file:
            return
        q = self.question.text().strip()
        if not q:
            show_toast(self, "اكتب سؤالاً أولاً", "warning")
            return
        self._start(ask_about_document, self.selected_file, q)

    def _summarize(self):
        if not self.selected_file:
            return
        self._start(summarize_document, self.selected_file)

    def _ok(self, text):
        self.progress.setVisible(False)
        self.ask_btn.setEnabled(True)
        self.summarize_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.answer.setPlainText(text or tr_text("(لا توجد إجابة)"))
        show_toast(self, tr_text("تمت الإجابة"), "success")

    def _fail(self, err):
        self.progress.setVisible(False)
        self.ask_btn.setEnabled(True)
        self.summarize_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.answer.setPlainText(tr_fmt("خطأ: {err}", err=tr_text(str(err))))
        show_toast(self, str(err), "error")
