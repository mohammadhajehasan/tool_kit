"""دعم لغتين: العربية (افتراضي) والإنجليزية.

التبديل يحفظ الاختيار في settings.json ويتطلب إعادة تشغيل التطبيق
(تُبنى الواجهة بنصوص اللغة المختارة واتجاهها المناسب).
"""

import json
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(_BASE, "settings.json")


def _detect_lang() -> str:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            lang = json.load(f).get("language", "ar")
        return lang if lang in ("ar", "en") else "ar"
    except Exception:
        return "ar"


_LANG = _detect_lang()

STRINGS = {
    "ar": {
        # الترويسة والشريط الجانبي
        "app_title": "PDF Toolbox — أداة PDF",
        "app_name": "أداة PDF",
        "app_subtitle": "كل الأدوات في مكان واحد",
        "theme_auto": "⚙️ تلقائي ({mode})",
        "theme_dark": "🌙 داكن",
        "theme_light": "☀️ فاتح",
        "lang_btn": "🌐 English",
        "lang_switch_msg": "سيتم إعادة تشغيل التطبيق لتطبيق اللغة الجديدة.",
        "restart_now": "إعادة التشغيل الآن",
        "later": "لاحقاً",
        # الأقسام
        "sec_core": "الأدوات الأساسية",
        "sec_convert": "التحويل والاستخراج",
        "sec_edit": "التحرير والحماية",
        "sec_extra": "أدوات إضافية",
        "sec_system": "النظام",
        # أسماء الأدوات
        "t_compress": "🗜️   ضغط PDF",
        "t_split": "✂️   تقطيع PDF",
        "t_merge": "🔗   دمج PDF",
        "t_convert": "🖼️   صور إلى PDF",
        "t_pdf2img": "📤   PDF إلى صور",
        "t_extract": "📃   نصوص وصور",
        "t_export": "📊   تصدير Word/Excel",
        "t_diff": "⚖️   مقارنة PDF",
        "t_ai": "🤖   مساعد ذكي",
        "t_ocr": "🔍   OCR",
        "t_pages": "✏️   محرر الصفحات",
        "t_stamp": "💧   علامة وترقيم",
        "t_protect": "🔒   الحماية",
        "t_repair": "🩺   إصلاح",
        "t_archive": "📦   فك ضغط",
        "t_info": "ℹ️   معلومات",
        "t_developer": "👨‍💻   المطور",
        # عناوين وأوصاف التبويبات الجديدة
        "pdf2img_title": "تحويل PDF إلى صور",
        "pdf2img_desc": "صدّر صفحات ملف PDF كصور JPG أو PNG بجودة ودقة تختارها",
        "extract_title": "استخراج النصوص والصور",
        "extract_desc": "انسخ نص الملف كاملاً إلى ملف نصي، أو أخرج كل الصور المضمّنة بجودتها الأصلية",
        "pages_title": "محرر الصفحات",
        "pages_desc": "أعد ترتيب الصفحات بالسحب، ودوّرها، واحذف ما لا تريد — ثم احفظ النتيجة",
        "stamp_title": "علامة مائية وترقيم",
        "stamp_desc": "اطبع علامة مائية نصية أو صورة على كل الصفحات، ورقّمها تلقائياً",
        "protect_title": "حماية ملفات PDF",
        "protect_desc": "شفّر ملفك بكلمة مرور (AES-256) مع أذونات تحكم، أو أزل الحماية عن ملف تملكه",
        "ocr_title": "التعرف الضوئي OCR",
        "ocr_desc": "حوّل الصفحات الممسوحة إلى PDF قابل للبحث والنسخ (عربي/إنجليزي)",
        "repair_title": "إصلاح ملف تالف",
        "repair_desc": "إذا رفض تطبيق آخر فتح ملفك، جرّب إصلاحه هنا قبل أن تستسلم له",
        "update_title": "🔔 يوجد تحديث جديد",
        "update_body": "الإصدار {latest} متوفر الآن — نسختك الحالية {current}",
        "update_btn": "⬇️ تحميل الإصدار الجديد",
        "update_later": "لاحقاً",
        "uptodate": "✅ أنت تستخدم أحدث إصدار",
        "check_updates": "🔄 فحص التحديث الآن",
        "palette_title": "الانتقال السريع",
        "palette_hint": "اكتب اسم أداة ثم Enter…",
        "activity_title": "🕘  سجل نشاطك",
        "activity_stats": "📁 عالجت {n} ملفاً  •  💾 وفّرت {size} بالضغط",
        "activity_none": "لا عمليات بعد — ابدأ بأول عملية وسجّلها هنا",
        # أزرار مشتركة
        "run": "تنفيذ",
        "save_result": "💾 حفظ النتيجة",
        "open_folder": "📂 فتح مجلد النتيجة",
        "done": "اكتملت العملية بنجاح",
        "ready": "جاهز",
        "cancel": "إلغاء",
    },
    "en": {
        "app_title": "PDF Toolbox",
        "app_name": "PDF Toolbox",
        "app_subtitle": "All tools in one place",
        "theme_auto": "⚙️ Auto ({mode})",
        "theme_dark": "🌙 Dark",
        "theme_light": "☀️ Light",
        "lang_btn": "🌐 العربية",
        "lang_switch_msg": "The app will restart to apply the new language.",
        "restart_now": "Restart now",
        "later": "Later",
        "sec_core": "Core tools",
        "sec_convert": "Convert & extract",
        "sec_edit": "Edit & protect",
        "sec_extra": "More tools",
        "sec_system": "System",
        "t_compress": "🗜️   Compress PDF",
        "t_split": "✂️   Split PDF",
        "t_merge": "🔗   Merge PDF",
        "t_convert": "🖼️   Images to PDF",
        "t_pdf2img": "📤   PDF to Images",
        "t_extract": "📃   Text & Images",
        "t_export": "📊   Export Word/Excel",
        "t_diff": "⚖️   Compare PDFs",
        "t_ai": "🤖   AI Assistant",
        "t_ocr": "🔍   OCR",
        "t_pages": "✏️   Page Editor",
        "t_stamp": "💧   Stamp & Number",
        "t_protect": "🔒   Protection",
        "t_repair": "🩺   Repair",
        "t_archive": "📦   Extract Archives",
        "t_info": "ℹ️   About",
        "t_developer": "👨‍💻   Developer",
        "pdf2img_title": "PDF to Images",
        "pdf2img_desc": "Export PDF pages as JPG/PNG images with your chosen quality and DPI",
        "extract_title": "Extract Text & Images",
        "extract_desc": "Copy the full text into a .txt file, or pull out every embedded image at full quality",
        "pages_title": "Page Editor",
        "pages_desc": "Reorder pages by drag & drop, rotate them, delete what you don't need — then save",
        "stamp_title": "Watermark & Numbering",
        "stamp_desc": "Stamp a text or image watermark on every page, and number them automatically",
        "protect_title": "PDF Protection",
        "protect_desc": "Encrypt your file with a password (AES-256) and permissions, or remove protection",
        "ocr_title": "OCR Recognition",
        "ocr_desc": "Turn scanned pages into a searchable, copyable PDF (Arabic/English)",
        "repair_title": "Repair a Broken File",
        "repair_desc": "If another app refuses to open your file, try repairing it here first",
        "update_title": "🔔 Update available",
        "update_body": "Version {latest} is available — you have {current}",
        "update_btn": "⬇️ Download update",
        "update_later": "Later",
        "uptodate": "✅ You're up to date",
        "check_updates": "🔄 Check for updates",
        "palette_title": "Quick Jump",
        "palette_hint": "Type a tool name then Enter…",
        "activity_title": "🕘  Your activity",
        "activity_stats": "📁 Processed {n} files  •  💾 Saved {size} by compressing",
        "activity_none": "No operations yet — your history will appear here",
        "run": "Run",
        "save_result": "💾 Save result",
        "open_folder": "📂 Open output folder",
        "done": "Operation completed successfully",
        "ready": "Ready",
        "cancel": "Cancel",
    },
}


def lang() -> str:
    return _LANG


def rtl() -> bool:
    return _LANG == "ar"


def set_lang(value: str):
    """يحفظ اللغة في الإعدادات (يُطبق بعد إعادة التشغيل)."""
    global _LANG
    _LANG = value if value in ("ar", "en") else "ar"
    try:
        data = {}
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["language"] = _LANG
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def tr(key: str) -> str:
    """ترجمة مفتاح — يعود للعربية إن لم توجد الترجمة."""
    return STRINGS.get(_LANG, STRINGS["ar"]).get(key) or STRINGS["ar"].get(key, key)


def tr_text(text: str) -> str:
    """يترجم نصاً عربياً ظاهراً للواجهة (ثابت أو ديناميكي) عند تفعيل الإنجليزية."""
    if _LANG != "en" or not text:
        return text
    from ui.en_text import lookup
    return lookup(text)


def tr_fmt(template: str, **kwargs) -> str:
    """يترجم قالباً عربياً يحتوي {placeholders} ثم يملؤه."""
    return tr_text(template).format(**kwargs)


def translate_widget_tree(root):
    """يترجم كل النصوص الظاهرة في شجرة ودجات بُنيت بالعربية.

    يُستدعى مرة واحدة بعد بناء الواجهة (وعند الإنجليزية فقط). لا يلمس
    محتوى حقول الإدخال أو بيانات المستخدم — النصوص فقط.
    """
    if _LANG != "en" or root is None:
        return
    from PySide6.QtWidgets import (
        QWidget, QLabel, QAbstractButton, QLineEdit, QTextEdit,
        QPlainTextEdit, QComboBox, QListWidget, QTabWidget, QGroupBox,
    )

    widgets = [root] + root.findChildren(QWidget)
    for w in widgets:
        try:
            if isinstance(w, QLabel):
                _retranslate(w, "text", "setText")
            elif isinstance(w, QAbstractButton):
                _retranslate(w, "text", "setText")
            elif isinstance(w, QLineEdit):
                _retranslate(w, "placeholderText", "setPlaceholderText")
            elif isinstance(w, (QTextEdit, QPlainTextEdit)):
                _retranslate(w, "placeholderText", "setPlaceholderText")
            elif isinstance(w, QTabWidget):
                for i in range(w.count()):
                    w.setTabText(i, tr_text(w.tabText(i)))
            elif isinstance(w, QGroupBox):
                _retranslate(w, "title", "setTitle")

            # التلميحات
            tip = w.toolTip()
            if tip:
                w.setToolTip(tr_text(tip))

            # العناصر المنسدلة
            if isinstance(w, QComboBox):
                for i in range(w.count()):
                    w.setItemText(i, tr_text(w.itemText(i)))
            elif isinstance(w, QListWidget):
                for i in range(w.count()):
                    item = w.item(i)
                    if item is not None:
                        item.setText(tr_text(item.text()))
                        if item.toolTip():
                            item.setToolTip(tr_text(item.toolTip()))

            # عنوان النافذة
            title = w.windowTitle()
            if title:
                w.setWindowTitle(tr_text(title))
        except (RuntimeError, AttributeError):
            continue


def _retranslate(widget, getter: str, setter: str):
    """يقرأ خاصية نصية ويستبدلها إن وُجدت ترجمة مختلفة."""
    value = getattr(widget, getter)()
    new_value = tr_text(value)
    if new_value != value:
        getattr(widget, setter)(new_value)
