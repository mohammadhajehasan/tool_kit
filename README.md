# 📄 PDF Toolbox — أداة PDF

تطبيق سطح مكتب عربي لمعالجة ملفات PDF: ضغط، تقطيع، دمج، وتحويل صور إلى PDF.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.11-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ المميزات

| الأداة | الوصف |
|--------|-------|
| 🗜️ **ضغط PDF** | تقليل حجم الملف مع الحفاظ على قابلية القراءة (PyMuPDF / Ghostscript / pikepdf) |
| ✂️ **تقطيع PDF** | استخراج صفحات محددة أو تقسيم كل صفحة لملف مستقل، مع معاينة مصغّرة تفاعلية |
| 🔗 **دمج PDF** | دمج عدة ملفات في ملف واحد مع إعادة ترتيب بالسحب |
| 🖼️ **صور إلى PDF** | تحويل JPG, PNG, BMP, TIFF, WEBP, GIF إلى PDF واحد |

## 🎨 التصميم

- واجهة عربية كاملة (RTL) بتصميم Modern Flat
- ثيمان قابلان للتبديل: بنفسجي / وردي
- منطقة سحب وإفلات (Drag & Drop) لكل الأدوات
- عمليات غير متزامنة لا تُجمّد الواجهة

## 📥 تحميل

حمّل أحدث نسخة جاهزة (exe) من صفحة [Releases](../../releases).

## 🚀 التشغيل من المصدر

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل التطبيق
python main.py
```

## 📦 بناء الـ exe

```bash
pyinstaller PDF_Toolbox.spec
```

## 🏗️ البنية

```
pdf_toolbox/
├── main.py                 # نقطة الدخول
├── core/                   # منطق المعالجة (بلا اعتماد على الواجهة)
│   ├── compress.py         # الضغط (PyMuPDF / Ghostscript / pikepdf)
│   ├── split.py            # التقطيع (pypdf)
│   ├── merge.py            # الدمج (pypdf)
│   └── convert.py          # تحويل الصور (img2pdf)
├── ui/                     # واجهة PySide6
│   ├── main_window.py      # النافذة الرئيسية
│   ├── compress_tab.py     # تبويب الضغط
│   ├── split_tab.py        # تبويب التقطيع
│   ├── merge_tab.py        # تبويب الدمج
│   ├── convert_tab.py      # تبويب التحويل
│   ├── widgets.py          # مكونات مشتركة (DropZone, Worker...)
│   ├── styles.py           # تنسيقات QSS
│   └── gender_dialog.py    # حوار اختيار الثيم
├── resources/              # الأيقونات
├── requirements.txt
└── PDF_Toolbox.spec        # إعداد PyInstaller
```

## 📚 المكتبات المستخدمة

- **PySide6** — إطار الواجهة الرسومية (Qt)
- **PyMuPDF (fitz)** — معالجة وضغط PDF
- **pypdf** — تقطيع ودمج PDF
- **img2pdf** — تحويل الصور إلى PDF
- **Pillow (PIL)** — معالجة الصور
- **pikepdf** — ضغط احتياطي لـ PDF
- **matplotlib** — الرسوم البيانية في تبويب الضغط

## 📄 الترخيص

MIT License
