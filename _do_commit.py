# كوميت المرحلة الأولى: النواة والواجهة للإصدار 2.0.0
import subprocess

MSG = """إضافة 9 أدوات جديدة + تحديثات كبرى للإصدار 2.0.0

أدوات جديدة في النواة (core/):
- pdf2img: تحويل PDF إلى صور JPG/PNG
- pages: محرر صفحات (إعادة ترتيب/تدوير/حذف)
- protect: تشفير AES-256 وإزالة الحماية عبر pikepdf
- stamp: علامة مائية عربية + ترقيم صفحات
- extract: استخراج النصوص والصور
- repair: إصلاح ملفات تالفة (pikepdf + PyMuPDF)
- history: سجل نشاط وإحصائيات في settings.json
- logger: سجل أخطاء متناوب + معالج استثناءات عام

تحسينات النواة:
- compress: مستوى ثالث "خفيف" + تقدير الحجم قبل الضغط
- split: تقسيم حسب الفهرس (الفصول) + معاينات آمنة الأسماء
- ocr: OCR اختياري عبر Tesseract (عربي/إنجليزي)

واجهة جديدة (ui/):
- 9 تبويبات جديدة لكل أداة + شريط جانبي بأقسام
- i18n: ترجمة عربي/إنجليزي مع اتجاه LTR للإنجليزية
- فاحص تحديث GitHub (فحص تلقائي عند الإقلاع + F5)
- لوحة انتقال سريع Ctrl+K + اختصارات Ctrl+1..0
- بطاقة نشاط في تبويب معلومات + زر فحص تحديث

main.py: واجهة سطر أوامر بـ9 أوامر + إعادة تشغيل عند تغيير اللغة
version.py: مركز معلومات الإصدار (2.0.0)
"""

r = subprocess.run(
    ["git", "add", "-A"],
    cwd=".",
    capture_output=True, text=True,
)
with open("_commit_msg.txt", "w", encoding="utf-8") as f:
    f.write(MSG)
r = subprocess.run(
    ["git", "commit", "-F", "_commit_msg.txt"],
    capture_output=True, text=True, shell=False,
)
print(r.stdout[-1200:])
print(r.stderr[-800:])
