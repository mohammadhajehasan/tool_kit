"""تبويب معلومات — شرح النظام وطريقة عمله ومعلومات عنه"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


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

        title = QLabel("معلومات عن النظام")
        title.setObjectName("pageTitle")
        desc = QLabel("كل ما تحتاج معرفته عن أداة PDF وكيف تعمل تحت الغطاء")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        # بطاقة التعريف
        layout.addWidget(AboutCard(
            "📄",
            "ما هو أداة PDF؟",
            "أداة PDF هو تطبيق سطح مكتب عربي يجمع أدوات معالجة ملفات PDF الأكثر "
            "استخداماً في نافذة واحدة أنيقة: ضغط، تقطيع، دمج، تحويل الصور، وفك ضغط "
            "الأرشيفات. كل العمليات تتم محلياً على جهازك بالكامل — لا يُرفع أي ملف "
            "إلى الإنترنت، ما يضمن خصوصيتك التامة.",
        ))

        # بطاقة كيف يعمل
        layout.addWidget(AboutCard(
            "⚙️",
            "كيف يعمل النظام؟",
            "يعمل النظام بثلاث طبقات منفصلة:\n"
            "• الواجهة (ui/) — مبنية بـ PySide6 (Qt) مع نظام تصميم يدعم الوضع الفاتح والداكن والتلقائي.\n"
            "• قلب المعالجة (core/) — دوال خالصة لا تعتمد على الواجهة، تستخدم محركات "
            "مثل PyMuPDF وpypdf وpy7zr حسب المهمة.\n"
            "• الخيوط المنفصلة (Worker) — كل عملية ثقيلة تعمل في خيط مستقل، فتبقى "
            "الواجهة سلسة وستبقى قابلة للاستخدام أثناء المعالجة، ويتحدث شريط التقدم لحظياً.",
        ))

        # بطاقة الأدوات
        layout.addWidget(AboutCard(
            "🧰",
            "الأدوات المتوفرة",
            "🗜️ ضغط PDF — يقلّص حجم الملف عبر PyMuPDF أو Ghostscript أو pikepdf مع رسم بياني مقارن.\n"
            "✂️ تقطيع PDF — اختر الصفحات بالنقر على المعاينة أو اكتب نطاقات مثل 1-3,5,8-10.\n"
            "🔗 دمج PDF — اسحب الملفات وأعد ترتيبها ثم ادمجها في ملف واحد.\n"
            "🖼️ صور إلى PDF — حوّل JPG/PNG/BMP/TIFF/WEBP/GIF إلى PDF.\n"
            "📦 فك ضغط — ZIP وCBZ وTAR (gz/bz2/xz) وGZ/BZ2/XZ، و7z وRAR عبر مكتبات اختيارية.",
        ))

        # بطاقة الخصوصية والأمان
        layout.addWidget(AboutCard(
            "🔒",
            "الخصوصية والأمان",
            "يعمل التطبيق دون اتصال بالإنترنت تماماً في معالجة الملفات. لا تجمع بيانات، "
            "لا إعلانات، ولا تتبع. ملفاتك لا تغادر جهازك أبداً. كذلك يحمي فك الضغط من "
            "مسارات الخروج الخبيثة (Zip-Slip) ويصحح أسماء الملفات العربية المشوهة.",
        ))

        # بطاقة الإصدار والترخيص
        layout.addWidget(AboutCard(
            "📜",
            "الإصدار والترخيص",
            "الإصدار الحالي: v1.2.0 — مفتوح المصدر برخصة MIT، ما يعني حرية الاستخدام "
            "والتعديل والتوزيع بشرط الإشارة إلى المرجع. للإبلاغ عن مشكلة أو اقتراح ميزة، "
            "تواصل مع المطور من تبويب «عن المطور».",
        ))

        layout.addStretch()
