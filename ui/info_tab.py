"""تبويب معلومات — شرح النظام، سجل النشاط، والإصدار"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt

from ui.i18n import tr
from core.history import get_activity, format_size
from version import APP_VERSION


class AboutCard(QFrame):
    """بطاقة نصية أنيقة لعنصر شرح"""

    def __init__(self, icon: str, title: str, body: str, parent=None):
        super().__init__(parent)
        self.setObjectName("aboutCard")
        self.setCursor(Qt.ArrowCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        head = QLabel(f"{icon}  {title}")
        head.setObjectName("cardTitle")
        head.setTextInteractionFlags(Qt.TextBrowserInteraction)
        layout.addWidget(head)

        text = QLabel(body)
        text.setObjectName("cardBody")
        text.setWordWrap(True)
        text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        layout.addWidget(text)


class InfoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("معلومات عن النظام" if tr("app_name") == "أداة PDF" else "About the System")
        title.setObjectName("pageTitle")
        desc = QLabel(
            "كل ما تحتاج معرفته عن أداة PDF وكيف تعمل تحت الغطاء"
            if tr("app_name") == "أداة PDF" else
            "Everything you need to know about PDF Toolbox and how it works"
        )
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        # بطاقة سجل النشاط (من settings.json)
        layout.addWidget(self._activity_card())

        ar = tr("app_name") == "أداة PDF"

        layout.addWidget(AboutCard(
            "📄",
            "ما هو أداة PDF؟" if ar else "What is PDF Toolbox?",
            ("أداة PDF هو تطبيق سطح مكتب عربي يجمع أدوات معالجة ملفات PDF الأكثر "
             "استخداماً في نافذة واحدة أنيقة: ضغط، تقطيع، دمج، تحويل الصور، فك ضغط "
             "الأرشيفات، استخراج النصوص والصور، محرر صفحات، علامة مائية، حماية، وOCR. "
             "كل العمليات تتم محلياً على جهازك بالكامل — لا يُرفع أي ملف إلى الإنترنت."
             if ar else
             "PDF Toolbox is a desktop app that puts the most-used PDF tools in one "
             "elegant window: compress, split, merge, image conversion, archive "
             "extraction, text/image extraction, page editor, watermarks, protection "
             "and OCR. Everything runs locally — no file ever leaves your device."),
        ))

        layout.addWidget(AboutCard(
            "⚙️",
            "كيف يعمل النظام؟" if ar else "How does it work?",
            ("يعمل النظام بثلاث طبقات منفصلة:\n"
             "• الواجهة (ui/) — مبنية بـ PySide6 (Qt) مع نظام تصميم يدعم الوضع الفاتح والداكن والتلقائي.\n"
             "• قلب المعالجة (core/) — دوال خالصة لا تعتمد على الواجهة، تستخدم محركات "
             "مثل PyMuPDF وpypdf وpikepdf وpy7zr حسب المهمة.\n"
             "• الخيوط المنفصلة (Worker) — كل عملية ثقيلة تعمل في خيط مستقل، فتبقى "
             "الواجهة سلسة، ويتحدث شريط التقدم لحظياً."
             if ar else
             "The system has three separated layers:\n"
             "• UI (ui/) — built with PySide6 (Qt) with a design system supporting light/dark/auto themes.\n"
             "• Core (core/) — pure functions without UI dependencies, using engines "
             "like PyMuPDF, pypdf, pikepdf and py7zr.\n"
             "• Worker threads — every heavy task runs on its own thread, keeping the "
             "UI smooth with live progress."),
        ))

        layout.addWidget(AboutCard(
            "🧰",
            "الأدوات المتوفرة" if ar else "Available tools",
            ("🗜️ ضغط — ثلاثة مستويات + تقدير حجم قبل الحفظ ورسم بياني مقارن.\n"
             "✂️ تقطيع — نطاقات يدوية، نقرة على المعاينة، أو تقسيم تلقائي حسب الفصول.\n"
             "✏️ محرر الصفحات — إعادة ترتيب بالسحب، تدوير، وحذف.\n"
             "🔗 دمج — عدة ملفات في واحد مع إعادة ترتيب.\n"
             "🖼️ صور إلى PDF / 📤 PDF إلى صور — تحويل بالاتجاهين.\n"
             "📃 نصوص وصور — استخراج نص الملف أو كل صوره.\n"
             "💧 علامة وترقيم — علامة مائية نصية أو صورة + ترقيم تلقائي.\n"
             "🔒 حماية — تشفير AES-256 مع أذونات، أو إزالة الحماية.\n"
             "🔍 OCR — صفحات ممسوحة تصبح قابلة للبحث (عربي/إنجليزي).\n"
             "🩺 إصلاح — إنقاذ ملفات PDF التالفة.\n"
             "📦 فك ضغط — ZIP وTAR و7z وRAR وغيرها."
             if ar else
             "🗜️ Compress — three levels + size estimate and before/after chart.\n"
             "✂️ Split — manual ranges, click-to-select, or auto-split by bookmarks.\n"
             "✏️ Page editor — drag to reorder, rotate, delete.\n"
             "🔗 Merge — many files into one with reordering.\n"
             "🖼️ Images to PDF / 📤 PDF to Images — both directions.\n"
             "📃 Text & images — extract file text or all embedded images.\n"
             "💧 Stamp & number — text/image watermark + automatic numbering.\n"
             "🔒 Protection — AES-256 encryption with permissions, or removal.\n"
             "🔍 OCR — scanned pages become searchable (Arabic/English).\n"
             "🩺 Repair — rescue broken PDF files.\n"
             "📦 Archives — ZIP, TAR, 7z, RAR and more."),
        ))

        layout.addWidget(AboutCard(
            "🔒",
            "الخصوصية والأمان" if ar else "Privacy & security",
            ("يعمل التطبيق دون اتصال بالإنترنت في معالجة الملفات. لا تجمع بيانات، "
             "لا إعلانات، ولا تتبع. ملفاتك لا تغادر جهازك أبداً. الاتصال الوحيد هو "
             "فحص التحديث (استعلام واحد هادئ عند الإقلاع). كما يحمي فك الضغط من "
             "مسارات الخروج الخبيثة (Zip-Slip) ويصحح أسماء الملفات العربية المشوهة."
             if ar else
             "The app processes files fully offline — no data collection, no ads, "
             "no tracking. Your files never leave your device. The only network "
             "call is a silent update check at startup."),
        ))

        # بطاقة الإصدار + فحص التحديث
        version_card = QFrame()
        version_card.setObjectName("aboutCard")
        vlayout = QVBoxLayout(version_card)
        vlayout.setContentsMargins(20, 16, 20, 16)
        vlayout.setSpacing(8)
        vhead = QLabel(f"📜  {'الإصدار والترخيص' if ar else 'Version & license'}")
        vhead.setObjectName("cardTitle")
        vbody = QLabel(
            (f"الإصدار الحالي: v{APP_VERSION} — مفتوح المصدر برخصة MIT. "
             "للإبلاغ عن مشكلة أو اقتراح ميزة، تواصل مع المطور من تبويب «عن المطور»."
             if ar else
             f"Current version: v{APP_VERSION} — open source under the MIT license. "
             "To report a problem or suggest a feature, reach the developer from the "
             "«Developer» tab."))
        vbody.setObjectName("cardBody")
        vbody.setWordWrap(True)
        self.check_btn = QPushButton(tr("check_updates"))
        self.check_btn.setObjectName("secondaryBtn")
        self.check_btn.clicked.connect(self._check_updates)
        vlayout.addWidget(vhead)
        vlayout.addWidget(vbody)
        vlayout.addWidget(self.check_btn)
        layout.addWidget(version_card)

        layout.addStretch()

    # ---------- بطاقة النشاط ----------
    def _activity_card(self) -> QFrame:
        ar = tr("app_name") == "أداة PDF"
        card = QFrame()
        card.setObjectName("aboutCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(6)

        head = QLabel("🕘  " + tr("activity_title").replace("🕘  ", ""))
        head.setObjectName("cardTitle")
        v.addWidget(head)

        act = get_activity()
        if act["processed"]:
            line = tr("activity_stats").format(
                n=act["processed"], size=format_size(act["saved_bytes"]))
            stats = QLabel(line)
            stats.setObjectName("cardBody")
            v.addWidget(stats)

            for r in act["recent"][:5]:
                import os
                name = os.path.basename(r.get("path", "")) or r.get("path", "")
                row = QLabel(f"  •  [{r.get('time', '')}] {r.get('tool', '')} — {name}")
                row.setObjectName("hintLabel")
                row.setToolTip(r.get("path", ""))
                v.addWidget(row)
        else:
            none_lbl = QLabel("  •  " + tr("activity_none"))
            none_lbl.setObjectName("hintLabel")
            v.addWidget(none_lbl)
        return card

    def _check_updates(self):
        from ui.update_checker import check_for_update
        check_for_update(self, notify_uptodate=True)
