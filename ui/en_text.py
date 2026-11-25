"""English text catalog for the whole interface.

Every key is the Arabic source string exactly as it appears in the code.
`lookup()` first tries an exact match, then falls back to a few regex
patterns that cover dynamic messages (numbers, paths, file names…).
"""

import re

EN_TEXT = {
    # ================= مشترك =================
    "إلغاء": "Cancel",
    "تنفيذ": "Run",
    "حذف المحدد": "Remove selected",
    "مسح الكل": "Clear all",
    "فتح": "Open",
    "تنبيه": "Notice",
    "خطأ": "Error",
    "خطأ في تحديد الصفحات": "Page selection error",
    "غير معروف": "Unknown",
    "لا نتائج": "No results",
    "اللغة": "Language",
    "الدقة": "DPI",
    "الصيغة": "Format",
    "الجودة": "Quality",
    "الصفحات": "Pages",
    "النموذج:": "Model:",
    "الحجم": "Size",
    "اللون": "Color",
    "الزاوية": "Angle",
    "الشفافية": "Opacity",
    "الموضع": "Position",
    "ملف واحد": "Single file",
    "يدعم ملف واحد في كل مرة": "One file at a time",
    "يمكن اختيار عدة ملفات (ملفين على الأقل)": "Select multiple files (at least two)",
    "يمكن اختيار عدة صور بترتيب معيّن": "Select multiple images in any order",
    "يمكن اختيار عدة أرشيفات في المرة الواحدة": "Select multiple archives at once",
    "اختر الملفات": "Select files",
    "اختر ملف": "Select a file",
    "تم إلغاء العملية": "Operation cancelled",
    "داكن": "Dark",
    "فاتح": "Light",
    "تبديل الثيم": "Switch theme",
    "اللغة / Language": "Language",
    "اختر ملف PDF": "Choose a PDF file",
    "الرجاء اختيار ملف PDF فقط": "Please choose a PDF file only",
    "اسحب ملف PDF هنا أو انقر للاختيار": "Drag a PDF here or click to choose",
    "اسحب ملف PDF هنا": "Drag a PDF here",
    "اسحب الملفات هنا أو انقر للاختيار": "Drag files here or click to choose",
    "اسحب الملف التالف هنا": "Drag the damaged file here",
    "اسحب الأرشيفات هنا أو انقر للاختيار": "Drag archives here or click to choose",
    "اسحب الصور هنا أو انقر للاختيار": "Drag images here or click to choose",
    "ملف واحد فقط": "One file only",

    # أسماء الملفات الافتراضية
    "_مضغوط.pdf": "_compressed.pdf",
    "_صور": "_images",
    "_معدل.pdf": "_edited.pdf",
    "_مصلح.pdf": "_repaired.pdf",
    "_مقتطف.pdf": "_extract.pdf",
    "_محمي.pdf": "_protected.pdf",
    "_بدون_حماية.pdf": "_unprotected.pdf",
    "_نهائي.pdf": "_final.pdf",
    "_علامة_مؤقت.pdf": "_watermark_tmp.pdf",

    # ================= الترويسة والتبويبات =================
    "معلومات عن النظام": "About the System",
    "كل ما تحتاج معرفته عن أداة PDF وكيف تعمل تحت الغطاء":
        "Everything you need to know about PDF Toolbox and how it works",
    "الإصدار والترخيص": "Version & license",
    "عن المطور": "About the Developer",
    "صاحب الفضل في تصميم وتطوير هذا النظام":
        "The person behind the design and development of this system",
    "المهندس أحمد مصطفى الفرحات": "Eng. Ahmad Mustafa Al-Farhat",
    "مهندس علوم حاسب — تطوير برمجيات وأنظمة تعمل بالذكاء الاصطناعي":
        "Computer Engineer — Software development and AI-powered systems",
    "مصمم ومطور نظام أداة PDF بالكامل": "Designer and developer of PDF Toolbox",
    "معلومات التواصل": "Contact information",
    "الهاتف": "Phone",
    "واتساب": "WhatsApp",
    "البريد الإلكتروني": "Email",
    "© 2026 المهندس أحمد مصطفى الفرحات — جميع الحقوق محفوظة":
        "© 2026 Eng. Ahmad Mustafa Al-Farhat — All rights reserved",
    "📞  معلومات التواصل": "📞  Contact information",

    # ================= سجل النشاط =================
    "ضغط PDF": "Compress PDF",
    "استخراج نص": "Extract text",
    "استخراج صور": "Extract images",
    "PDF إلى صور": "PDF to Images",
    "محرر الصفحات": "Page Editor",
    "حماية PDF": "PDF Protection",
    "إصلاح PDF": "PDF Repair",
    "علامة مائية وترقيم": "Watermark & Numbering",

    # ================= ضغط =================
    "ضغط ملفات PDF": "Compress PDF Files",
    "قلّل حجم ملف PDF مع الحفاظ على المحتوى قابلاً للقراءة":
        "Reduce PDF size while keeping the content readable",
    "يدعم ملف واحد في كل مرة": "One file at a time",
    "ضغط خفيف": "Light compression",
    "أقل تدخّل ممكن — يحافظ على أعلى جودة ويقلّل الحجم قليلاً":
        "Minimal intervention — keeps the highest quality with a small size reduction",
    "الضغط الموصى به": "Recommended compression",
    "يقلّص حجم الملف إلى النصف تقريباً مع الحفاظ على جودة جيدة":
        "Cuts file size by about half while keeping good quality",
    "الضغط الشديد": "Extreme compression",
    "أقصى تقليص ممكن للحجم، قد يؤثر على جودة الصور والخطوط":
        "Maximum size reduction; may affect image and font quality",
    "استخدام Ghostscript لضغط أقوى (اختياري)":
        "Use Ghostscript for stronger compression (optional)",
    "يستخدم محرك Ghostscript للضغط، مع تحقق تلقائي من سلامة الملف قبل الحفظ":
        "Uses the Ghostscript engine with automatic file integrity checks before saving",
    "Ghostscript غير مثبّت على هذا الجهاز.\n"
    "سيتم استخدام PyMuPDF للضغط (فعّال أيضاً).\n"
    "لتفعيله: ثبّت Ghostscript أو ضع gswin64c.exe في resources/gs/":
        "Ghostscript is not installed on this device.\n"
        "PyMuPDF will be used for compression (also effective).\n"
        "To enable it: install Ghostscript or place gswin64c.exe in resources/gs/",
    "📏 تقدير الحجم": "📏 Estimate size",
    "ضغط الملف": "Compress file",
    "قبل الضغط": "Before",
    "بعد الضغط": "After",
    "الحجم (MB)": "Size (MB)",
    "⏳ جارٍ تقدير الحجم (تجربة الضغط على نسخة مؤقتة)…":
        "⏳ Estimating size (test-compressing a temporary copy)…",
    "📏 تقدير المستوى المحدد:  {orig} ← {est}  (توفير {pct}%)\n"
    "انقر «ضغط الملف» للحفظ الفعلي":
        "📏 Estimate for the selected level:  {orig} ← {est}  (saves {pct}%)\n"
        "Click “Compress file” to save",
    "حفظ الملف المضغوط": "Save compressed file",
    "⏳  جاري الضغط... يرجى الانتظار": "⏳  Compressing... please wait",
    "تم توفير {pct}% من الحجم": "Saved {pct}% of the size",
    "الملف مضغوط أصلاً — لم يتغيّر الحجم كثيراً":
        "The file is already compressed — size barely changed",
    "{emoji}  تم الضغط بنجاح عبر {method}\n\n"
    "    📊  الحجم الأصلي:    {orig}\n"
    "    📊  الحجم الجديد:    {comp}\n"
    "    📉  {pct_text}\n\n"
    "    💾  حُفظ في:  {output_path}":
        "{emoji}  Compression succeeded using {method}\n\n"
        "    📊  Original size:    {orig}\n"
        "    📊  New size:         {comp}\n"
        "    📉  {pct_text}\n\n"
        "    💾  Saved to:  {output_path}",
    "تم الضغط عبر {method} — توفير {pct}%":
        "Compressed with {method} — saved {pct}%",
    "❌  فشلت العملية:\n{error_msg}":
        "❌  Operation failed:\n{error_msg}",

    # ================= تقطيع =================
    "تقطيع ملف PDF": "Split PDF File",
    "استخرج صفحات محددة من ملف PDF — انقر على الصفحات لاختيارها أو أدخل النطاق يدوياً":
        "Extract specific pages from a PDF — click pages to select them or enter a range manually",
    "معاينة الصفحات — انقر على الصفحات لاختيارها:":
        "Page preview — click pages to select them:",
    "الصفحات المطلوبة:": "Pages to extract:",
    "مثال: 1-3,5,8-10": "e.g. 1-3,5,8-10",
    "دمج الصفحات المحددة في ملف واحد": "Merge selected pages into one file",
    "كل صفحة كملف مستقل": "Each page as a separate file",
    "📚 حسب الفهرس (الفصول)": "📚 By bookmarks (chapters)",
    "يتطلب ملفاً يحتوي إشارات إرشاد (فهرس/فصول)":
        "Requires a file with bookmarks (index/chapters)",
    "تقطيع الملف": "Split file",
    "لم يتم تحديد أي صفحات": "No pages selected",
    "عدد صفحات الملف: {n}": "Page count: {n}",
    "الملف يحتوي {n} فصلاً في المستوى الأول":
        "The file has {n} top-level chapters",
    "  •  📚 {n} فصلاً": "  •  📚 {n} chapters",
    "تم تحديد {n} صفحة": "{n} pages selected",
    "سيتم تحديد {n} صفحة": "{n} pages will be selected",
    "تعذّر قراءة الملف: {err}": "Could not read the file: {err}",
    "اختر مجلد الحفظ": "Choose output folder",
    "حفظ الملف الناتج": "Save output file",
    "جاري التقطيع...": "Splitting...",
    "✅ تم التقسيم إلى {n} ملف حسب الفصول\nحُفظت في: {output_dir}":
        "✅ Split into {n} files by chapters\nSaved to: {output_dir}",
    "✅ تم استخراج {n} صفحة بنجاح\nحُفظ في: {output_path}":
        "✅ Extracted {n} pages successfully\nSaved to: {output_path}",
    "✅ تم إنشاء {n} ملف مستقل\nحُفظت في: {output_dir}":
        "✅ Created {n} separate files\nSaved to: {output_dir}",
    "❌ فشلت العملية: {error_msg}": "❌ Operation failed: {error_msg}",

    # ================= دمج =================
    "دمج ملفات PDF": "Merge PDF Files",
    "ادمج عدة ملفات PDF في ملف واحد — اسحب لإعادة ترتيب الملفات قبل الدمج":
        "Merge several PDFs into one file — drag to reorder before merging",
    "اسحب ملفات PDF هنا أو انقر للاختيار":
        "Drag PDF files here or click to choose",
    "دمج الملفات": "Merge files",
    "تم تجاهل {skipped} ملف غير PDF":
        "Ignored {skipped} non-PDF files",
    "حفظ الملف المدموج": "Save merged file",
    "ملف_مدموج.pdf": "merged_file.pdf",
    "جاري الدمج...": "Merging...",
    "✅ تم دمج {count} ملفات بنجاح\nحُفظ في: {output_path}":
        "✅ Merged {count} files successfully\nSaved to: {output_path}",

    # ================= تحويل الصور =================
    "تحويل الصور إلى PDF": "Convert Images to PDF",
    "حوّل صورة واحدة أو عدة صور (JPG, PNG, BMP, WEBP...) إلى ملف PDF واحد":
        "Convert one or more images (JPG, PNG, BMP, WEBP...) into a single PDF",
    "تحويل إلى PDF": "Convert to PDF",
    "تم تجاهل {skipped} ملف بصيغة غير مدعومة":
        "Ignored {skipped} unsupported files",
    "حفظ ملف PDF": "Save PDF file",
    "صور_محولة.pdf": "converted_images.pdf",
    "جاري التحويل...": "Converting...",
    "✅ تم تحويل {count} صورة إلى PDF بنجاح\nحُفظ في: {output_path}":
        "✅ Converted {count} images to PDF successfully\nSaved to: {output_path}",
    "تم تحويل {count} صورة إلى PDF": "Converted {count} images to PDF",

    # ================= PDF إلى صور =================
    "تحويل PDF إلى صور": "PDF to Images",
    "صدّر صفحات ملف PDF كصور JPG أو PNG بجودة ودقة تختارها":
        "Export PDF pages as JPG or PNG images with your chosen quality and DPI",
    "اسحب ملف PDF هنا أو انقر للاختيار": "Drag a PDF here or click to choose",
    "ستُحفظ الصور في مجلد بجانب الملف":
        "Images will be saved to a folder next to the file",
    "عالية (92)": "High (92)",
    "متوازنة (80)": "Balanced (80)",
    "ملف صغير (60)": "Small file (60)",
    "شاشة (144)": "Screen (144)",
    "عالية (200)": "High (200)",
    "طباعة (300)": "Print (300)",
    "مثال: 1-3,5 (فارغ = كل الصفحات)":
        "e.g. 1-3,5 (empty = all pages)",
    "⏳ جارٍ التحويل…": "⏳ Converting…",
    "✅ تم تحويل {n} صفحة إلى صور": "✅ Converted {n} pages to images",
    "✅ {n} صورة في: {dir}": "✅ {n} images in: {dir}",
    "PDF إلى صور": "PDF to Images",

    # ================= استخراج =================
    "استخراج النصوص والصور": "Extract Text & Images",
    "انسخ نص الملف كاملاً إلى ملف نصي، أو أخرج كل الصور المضمّنة بجودتها الأصلية":
        "Copy the full document text into a text file, or extract every embedded image at full quality",
    "📃  استخراج النص إلى ملف txt": "📃  Extract text to a TXT file",
    "🖼️  استخراج الصور المضمّنة": "🖼️  Extract embedded images",
    "⏳ جارٍ الاستخراج…": "⏳ Extracting…",
    "✅ استُخرج النص ({chars} حرفاً)":
        "✅ Extracted text ({chars} characters)",
    "✅ النص محفوظ في: {out}": "✅ Text saved to: {out}",
    "✅ استُخرجت {count} صورة": "✅ Extracted {count} images",
    "✅ {count} صورة في: {dir}": "✅ {count} images in: {dir}",

    # ================= تصدير Word/Excel =================
    "تصدير إلى Word / Excel": "Export to Word / Excel",
    "استخرج النصوص إلى DOCX أو الجداول إلى XLSX مع الحفاظ على البنية قدر الإمكان":
        "Export text to DOCX or tables to XLSX while preserving structure as much as possible",
    "تصدير": "Export",
    "حفظ Word": "Save Word",
    "حفظ Excel": "Save Excel",
    "جاري التصدير…": "Exporting…",
    "✅ تم التصدير إلى Word\n{res}": "✅ Exported to Word\n{res}",
    "✅ تم التصدير إلى Excel — {tables} جدول\n{output}":
        "✅ Exported to Excel — {tables} tables\n{output}",
    "تم التصدير": "Export complete",

    # ================= مقارنة =================
    "مقارنة ملفات PDF": "Compare PDF Files",
    "ارفع نسختين لعرض الفروقات: أحمر للحذف وأخضر للإضافة":
        "Load two versions to see the differences: red for deletions, green for additions",
    "الملف الأصلي (أ)": "Original file (A)",
    "الملف الجديد (ب)": "New file (B)",
    "قارن الآن": "Compare now",
    "جاري المقارنة…": "Comparing…",
    "اكتملت المقارنة": "Comparison complete",
    "أ: {a}\nب: {b}": "A: {a}\nB: {b}",
    "صفحات أ={a} | ب={b} — إضافات: {added} | حذف: {removed}":
        "Pages A={a} | B={b} — Added: {added} | Removed: {removed}",
    "❌ {err}": "❌ {err}",

    # ================= OCR =================
    "التعرف الضوئي OCR": "OCR Recognition",
    "حوّل الصفحات الممسوحة إلى PDF قابل للبحث والنسخ (عربي/إنجليزي)":
        "Turn scanned pages into a searchable, copyable PDF (Arabic/English)",
    "اسحب ملف PDF ممسوح ضوئياً هنا":
        "Drag a scanned PDF here",
    "الناتج: PDF يحتوي طبقة نص مخفية قابلة للبحث والنسخ":
        "Output: a PDF with a hidden, searchable and copyable text layer",
    "عربي + إنجليزي": "Arabic + English",
    "عربي فقط": "Arabic only",
    "إنجليزي فقط": "English only",
    "سريعة (150)": "Fast (150)",
    "متوازنة (200)": "Balanced (200)",
    "دقيقة (300)": "Accurate (300)",
    "⚙️  OCR غير مفعّل على هذا النظام": "⚙️  OCR is not enabled on this system",
    "لتفعيل OCR:\n"
    "1) ثبّت Tesseract OCR من: https://github.com/UB-Mannheim/tesseract/wiki\n"
    "2) أثناء التثبيت اختر حزمة اللغة العربية (Arabic) والإنجليزية\n"
    "3) ثبّت مكتبة بايثون: pip install pytesseract\n"
    "4) إذا لم يُعثر على tesseract.exe أضف مساره إلى متغير PATH":
        "To enable OCR:\n"
        "1) Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki\n"
        "2) During installation, select the Arabic and English language packs\n"
        "3) Install the Python package: pip install pytesseract\n"
        "4) If tesseract.exe is not found, add its path to the PATH variable",
    "⬇️ تحميل Tesseract OCR": "⬇️ Download Tesseract OCR",
    "OCR غير مفعّل — راجع خطوات التثبيت أدناه":
        "OCR is not enabled — see the installation steps below",
    "⏳ جارٍ التعرف على النص (قد يستغرق دقائق للملفات الكبيرة)…":
        "⏳ Recognizing text (may take minutes for large files)…",
    "✅ أصبح الملف قابلاً للبحث ({pages} صفحة)":
        "✅ The file is now searchable ({pages} pages)",
    "✅ محفوظ: {out}": "✅ Saved: {out}",
    # Unlimited-OCR (خادم بعيد)
    "المحرك:": "Engine:",
    "Tesseract (محلي)": "Tesseract (local)",
    "Unlimited-OCR (خادم)": "Unlimited-OCR (server)",
    "Unlimited-OCR (Ollama محلي)": "Unlimited-OCR (local Ollama)",
    "يتطلب تثبيت Ollama وتنزيل النموذج: ollama pull richardyoung/unlimited-ocr":
        "Requires installing Ollama and pulling the model: ollama pull richardyoung/unlimited-ocr",
    "عنوان الخادم:": "Server URL:",
    "اسم النموذج:": "Model name:",
    "مفتاح API (اختياري)": "API key (optional)",
    "اتركه فارغاً إن لم يكن الخادم يتطلب مفتاحاً":
        "Leave empty if the server does not require a key",
    "فحص الاتصال": "Test connection",
    "⏳ جارٍ فحص الاتصال…": "⏳ Testing connection…",
    "✅ الخادم متصل": "✅ Server connected",
    "✅ الخادم متصل — النماذج: {models}": "✅ Server connected — models: {models}",
    "تم الاتصال بالخادم": "Connected to the server",
    "❌ تعذّر الاتصال: {err}": "❌ Connection failed: {err}",
    "أدخل عنوان الخادم واسم النموذج أولاً":
        "Enter the server URL and model name first",
    "⏳ جارٍ استخراج النص عبر Unlimited-OCR (قد يستغرق دقائق)…":
        "⏳ Extracting text with Unlimited-OCR (may take minutes)…",
    "⏳ جارٍ بناء PDF قابل للبحث…": "⏳ Building a searchable PDF…",
    "📝 النص أيضاً في: {out}": "📝 Text also saved to: {out}",
    "📝 النص محفوظ في: {out}": "📝 Text saved to: {out}",
    "✅ استُخرج النص ({pages} صفحة)": "✅ Text extracted ({pages} pages)",
    "⚠️ اضبط خادم Unlimited-OCR في تبويب OCR أولاً":
        "⚠️ Configure the Unlimited-OCR server in the OCR tab first",
    "استخدم Unlimited-OCR للمستندات الممسوحة تلقائياً":
        "Use Unlimited-OCR automatically for scanned documents",
    "يتطلب ضبط خادم Unlimited-OCR في تبويب OCR":
        "Requires configuring the Unlimited-OCR server in the OCR tab",
    "reportlab غير مثبّت أو لا يوجد خط عربي — حُفظ النص فقط":
        "reportlab is not installed or no Arabic font was found — only the text was saved",
    "لا يوجد نص في نتيجة النموذج": "The model returned no text",

    # ================= محرر الصفحات =================
    "محرر الصفحات": "Page Editor",
    "أعد ترتيب الصفحات بالسحب، ودوّرها، واحذف ما لا تريد — ثم احفظ النتيجة":
        "Reorder pages by dragging, rotate them, delete what you don't need — then save",
    "ثم اسحب الصفحات لإعادة ترتيبها": "Then drag pages to reorder them",
    "↻  تدوير المحدد": "↻  Rotate selected",
    "🗑  حذف المحدد": "🗑  Delete selected",
    "↩  استرجاع الأصل": "↩  Restore original",
    "⏳ جارٍ توليد المعاينات…": "⏳ Generating previews…",
    "✅ {total} صفحة — اسحب لإعادة الترتيب، حدد صفحة للتدوير/الحذف":
        "✅ {total} pages — drag to reorder, select a page to rotate/delete",
    "صفحة {n}": "Page {n}",
    "الصفحة الأصلية رقم {n}": "Original page {n}",
    "الصفحة الأصلية رقم {n} (مدورة {deg}°)": "Original page {n} (rotated {deg}°)",
    " (مدورة {deg}°)": " (rotated {deg}°)",
    "حدد صفحة أو أكثر أولاً": "Select one or more pages first",
    "حدد الصفحات التي تريد حذفها": "Select the pages you want to delete",
    "لا يمكن حذف كل الصفحات — احذف بعضها فقط":
        "You cannot delete all pages — keep at least one",
    "📄 {count} من {total} صفحة": "📄 {count} of {total} pages",
    "لا توجد صفحات للحفظ": "No pages to save",
    "حفظ الملف الجديد": "Save new file",
    "⏳ جارٍ الحفظ…": "⏳ Saving…",
    "✅ تم حفظ الملف بنجاح": "✅ File saved successfully",
    "✅ محفوظ: {out}": "✅ Saved: {out}",

    # ================= علامة مائية وترقيم =================
    "علامة مائية وترقيم": "Watermark & Numbering",
    "اطبع علامة مائية نصية أو صورة على كل الصفحات، ورقّمها تلقائياً":
        "Stamp a text or image watermark on every page, and number them automatically",
    "💧  علامة مائية": "💧  Watermark",
    "نص العلامة المائية (يدعم العربية)": "Watermark text (supports Arabic)",
    "خفيفة جداً": "Very light",
    "خفيفة": "Light",
    "متوسطة": "Medium",
    "واضحة": "Clear",
    "صغير": "Small",
    "متوسط": "Medium",
    "كبير": "Large",
    "رمادي": "Gray",
    "أزرق": "Blue",
    "أحمر": "Red",
    "أسود": "Black",
    "نص فقط": "Text only",
    "صورة كعلامة مائية": "Image as watermark",
    "🖼️  اختر صورة…": "🖼️  Choose image…",
    "🔢  ترقيم الصفحات": "🔢  Page numbering",
    "صفحة 1 من 10": "Page 1 of 10",
    "وسط أسفل": "Bottom center",
    "يسار أسفل": "Bottom left",
    "يمين أسفل": "Bottom right",
    "وسط أعلى": "Top center",
    "اختر صورة العلامة المائية": "Choose watermark image",
    "أدخل نص العلامة المائية أو فعّل الترقيم":
        "Enter watermark text or enable numbering",
    "⏳ جارٍ التطبيق…": "⏳ Applying…",
    "✅ تم التطبيق": "✅ Applied",
    " (علامة مائية + ترقيم)": " (watermark + numbering)",
    " (ترقيم)": " (numbering)",

    # ================= حماية =================
    "حماية ملفات PDF": "PDF Protection",
    "شفّر ملفك بكلمة مرور (AES-256) مع أذونات تحكم، أو أزل الحماية عن ملف تملكه":
        "Encrypt your file with a password (AES-256) and permissions, or remove protection from a file you own",
    "🔒  تشفير بحماية": "🔒  Encrypt with protection",
    "🔓  إزالة الحماية": "🔓  Remove protection",
    "كلمة المرور": "Password",
    "تأكيد كلمة المرور": "Confirm password",
    "السماح بالطباعة": "Allow printing",
    "السماح بنسخ النص": "Allow copying text",
    "السماح بالتعديل": "Allow editing",
    "AES-256 — لا يمكن استعادة الملف إن نسيت كلمة المرور":
        "AES-256 — the file cannot be recovered if you forget the password",
    "📄 {name} — 🔒 محمي (سيُفعّل وضع فك الحماية)":
        "📄 {name} — 🔒 Protected (unprotect mode enabled)",
    "أدخل كلمة المرور أولاً": "Enter the password first",
    "كلمتا المرور غير متطابقتين": "Passwords do not match",
    "⏳ جارٍ التنفيذ…": "⏳ Processing…",
    "حُمي": "protected",
    "أُزيلت حمايته": "unprotected",
    "✅ {label} الملف بنجاح": "✅ File {label} successfully",

    # ================= إصلاح =================
    "إصلاح ملف تالف": "Repair a Broken File",
    "إذا رفض تطبيق آخر فتح ملفك، جرّب إصلاحه هنا قبل أن تستسلم له":
        "If another app refuses to open your file, try repairing it here first",
    "يعيد بناء بنية الملف: فهرس xref، الكائنات الناقصة، وترتيب الصفحات":
        "Rebuilds the file structure: xref index, missing objects, and page order",
    "🩺  إصلاح الملف": "🩺  Repair file",
    "⏳ جارٍ الإصلاح…": "⏳ Repairing…",
    "✅ أُصلح الملف عبر {engine}": "✅ File repaired using {engine}",
    "✅ محفوظ: {out} ({size} — المحرك: {engine})":
        "✅ Saved: {out} ({size} — engine: {engine})",

    # ================= الأرشيفات =================
    "فك ضغط الأرشيفات": "Extract Archives",
    "استخرج محتوى الأرشيفات المضغوطة — يدعم ZIP و7z وRAR وTAR وGZIP وغيرها":
        "Extract compressed archive contents — supports ZIP, 7z, RAR, TAR, GZIP and more",
    "بجانب كل أرشيف": "Next to each archive",
    "ينشئ مجلداً باسم الأرشيف نفسه بجوار مكان الملف":
        "Creates a folder named after the archive beside the file",
    "مجلد محدد": "Specific folder",
    "يستخرج محتوى كل الأرشيفات إلى مجلد واحد تختاره":
        "Extracts all archives into one folder you choose",
    "لم يُحدد مجلد بعد": "No folder selected yet",
    "📁 اختيار المجلد…": "📁 Choose folder…",
    "فتح مجلد النتيجة تلقائياً بعد الانتهاء":
        "Open the output folder automatically when done",
    "فك الضغط": "Extract",
    "ℹ️ صيغ تعمل بعد تثبيت مكتباتها الاختيارية: pip install {tips}":
        "ℹ️ Formats that work after installing their optional libraries: pip install {tips}",
    "اختر مجلد الإخراج": "Choose output folder",
    "اختر مجلد الإخراج أولاً": "Choose an output folder first",
    "⛔  تم تجاهل {n} ملف بصيغة غير مدعومة":
        "⛔  Ignored {n} unsupported files",
    "⏳  جاري فك ضغط الأرشيفات…": "⏳  Extracting archives…",
    "⏳  {msg}": "⏳  {msg}",
    "📦 فك ضغط: {name}": "📦 Extracting: {name}",
    "• {name}  →  {files} ملف": "• {name}  →  {files} files",
    "✅  تم فك ضغط {n} أرشيف بنجاح — إجمالي الملفات: {total}\n\n{lines}":
        "✅  Extracted {n} archives successfully — total files: {total}\n\n{lines}",
    "\n\n⚠️  فشل تحليل ما يلي:\n{lines}":
        "\n\n⚠️  Failed to process the following:\n{lines}",

    # ================= المساعد الذكي =================
    "المساعد الذكي للمستندات": "Smart Document Assistant",
    "تلخيص وأسئلة حول محتوى الملف — محلياً عبر Ollama أو بمفتاح API اختياري":
        "Summaries and questions about your document — locally via Ollama or an optional API key",
    "يُفضّل مستنداً فيه طبقة نص (أو بعد OCR)":
        "A document with a text layer (or after OCR) works best",
    "Ollama محلي": "Local Ollama",
    "API سحابي": "Cloud API",
    "مفتاح API (اختياري — يُحفظ محلياً)":
        "API key (optional — stored locally)",
    "اسأل عن المستند… مثال: ما أهم بنود العقد؟":
        "Ask about the document… e.g. What are the key contract terms?",
    "تلخيص": "Summarize",
    "اسأل": "Ask",
    "ستظهر الإجابة هنا…": "The answer will appear here…",
    "Ollama متصل محلياً": "Ollama connected locally",
    " — نماذج: {models}": " — models: {models}",
    "Ollama غير متصل. ثبّته من ollama.com ثم: ollama run llama3.2":
        "Ollama is not connected. Install it from ollama.com, then run: ollama run llama3.2",
    "وضع API: يُرسل النص إلى مزود متوافق مع OpenAI (اختياري)":
        "API mode: sends the text to an OpenAI-compatible provider (optional)",
    "جاري التفكير…": "Thinking…",
    "اكتب سؤالاً أولاً": "Type a question first",
    "(لا توجد إجابة)": "(No answer)",
    "تمت الإجابة": "Answer ready",
    "خطأ: {err}": "Error: {err}",
    "لا يوجد نص قابل للاستخراج في الملف.\n"
    "جرّب أولاً أداة OCR للمستندات الممسوحة.":
        "There is no extractable text in the file.\n"
        "Try the OCR tool for scanned documents first.",

    # ================= لوحة الأوامر =================
    "Enter للانتقال  •  Esc للإغلاق": "Enter to jump  •  Esc to close",

    # ================= التحديث =================
    "تعذر الاتصال بالإنترنت — تأكد من اتصالك ثم أعد المحاولة":
        "Could not connect to the internet — check your connection and try again",

    # ================= نافذة الخطأ =================
    "PDF Toolbox — خطأ غير متوقع": "PDF Toolbox — Unexpected error",
    "حدث خطأ غير متوقع وتم تسجيل التفاصيل في ملف السجل.":
        "An unexpected error occurred. Details were written to the log file.",
    "يمكنك إبلاغ المطور مع تفاصيل الخطأ.":
        "You can report the error to the developer with the details.",
    "📂 فتح ملف السجل": "📂 Open log file",
    "✉️ إبلاغ المطور": "✉️ Report to developer",
    "إغلاق": "Close",
    "PDF Toolbox v{version} — مشكلة": "PDF Toolbox v{version} — Problem",
    "السلام عليكم، واجهتني هذه المشكلة في التطبيق:\n\n(اشرح ما كنت تفعله)\n\n":
        "Hello, I ran into this problem in the app:\n\n(describe what you were doing)\n\n",
    "--- آخر السجل ---\n": "--- Last log entries ---\n",
}


# قوالب ديناميكية لا يمكن مطابقتها نصياً (أرقام/مسارات داخل الرسالة)
EN_PATTERNS = [
    # أخطاء شائعة من core
    (re.compile(r"^الملف غير موجود: (.+)$", re.S), r"File not found: \1"),
    (re.compile(r"^صيغة غير مدعومة: (.+)$", re.S), r"Unsupported format: \1"),
    (re.compile(r"^يجب اختيار ملفين على الأقل للدمج$"), "Select at least two files to merge"),
    (re.compile(r"^لم يتم اختيار أي صور$"), "No images selected"),
    (re.compile(r"^لا توجد صفحات صالحة$"), "No valid pages"),
    (re.compile(r"^لا توجد صفحات للمعالجة$"), "No pages to process"),
    (re.compile(r"^لم يتم إنشاء الملف الناتج$"), "The output file was not created"),
    (re.compile(r"^انتهت مهلة عملية الضغط \(الملف كبير جداً\)$"),
     "Compression timed out (file is too large)"),
    (re.compile(r"^أدخل نص العلامة المائية أو اختر صورة$"),
     "Enter watermark text or choose an image"),
    (re.compile(r"^أدخل مفتاح API أولاً$"), "Enter an API key first"),
    (re.compile(r"^PyMuPDF غير مثبّت\. ثبّته: pip install pymupdf$"),
     "PyMuPDF is not installed. Install it with: pip install pymupdf"),
    (re.compile(r"^ثبّت pdf2docx: pip install pdf2docx$"),
     "Install pdf2docx: pip install pdf2docx"),
    (re.compile(r"^ثبّت pdfplumber و openpyxl: pip install pdfplumber openpyxl$"),
     "Install pdfplumber and openpyxl: pip install pdfplumber openpyxl"),
    (re.compile(r"^فشل دمج الملف '(.+?)': (.+)$", re.S),
     r"Failed to merge file '\1': \2"),
    (re.compile(r"^فشل الضغط عبر (PyMuPDF|Ghostscript|pikepdf): (.+)$", re.S),
     r"Compression failed via \1: \2"),
    (re.compile(r"^فشل قراءة ملف PDF: (.+)$", re.S), r"Failed to read the PDF: \1"),
    (re.compile(r"^فشل التحويل إلى Word: (.+)$", re.S), r"Word conversion failed: \1"),
    (re.compile(r"^فشل حفظ Excel: (.+)$", re.S), r"Failed to save Excel: \1"),
    (re.compile(r"^تعذّر الاتصال بـ Ollama: (.+)$", re.S),
     r"Could not connect to Ollama: \1"),
    (re.compile(r"^فشل طلب API: (.+)$", re.S), r"API request failed: \1"),
    (re.compile(r"^خطأ API \((.+?)\): (.+)$", re.S), r"API error (\1): \2"),
    (re.compile(r"^مكتبة ناقصة: (.+)$", re.S), r"Missing library: \1"),
    (re.compile(r"^فشل التعرف على النص \(اللغة: (.+?)\)\.\n(.+)\n\n"
                r"تأكد من تثبيت حزم اللغات \(ara / eng\) في Tesseract\.$", re.S),
     r"OCR failed (language: \1).\n\2\n\n"
     r"Make sure the language packs (ara / eng) are installed in Tesseract."),
    (re.compile(r"^Ollama غير متاح محلياً\.\nثبّته من https://ollama\.com "
                r"وشغّل نموذجاً مثل: ollama run llama3\.2\n"
                r"أو استخدم وضع API السحابي الاختياري\.$"),
     "Ollama is not available locally.\n"
     "Install it from https://ollama.com and run a model such as: ollama run llama3.2\n"
     "Or use the optional cloud API mode."),
    # رسالة "خطأ: ..." العامة
    (re.compile(r"^خطأ: (.+)$", re.S), r"Error: \1"),
    # عناصر الصفحات (tooltips)
    (re.compile(r"^الصفحة الأصلية رقم (\d+)$"), r"Original page \1"),
    (re.compile(r"^الصفحة الأصلية رقم (\d+) \(مدورة (\d+)°\)$"),
     r"Original page \1 (rotated \2°)"),
    # رسالة التقدم في الأرشيف
    (re.compile(r"^📦 فك ضغط: (.+)$"), r"📦 Extracting: \1"),
    # Unlimited-OCR
    (re.compile(r"^Unlimited-OCR غير مُعدّ: أدخل عنوان الخادم واسم النموذج$"),
     "Unlimited-OCR is not configured: enter the server URL and model name"),
    (re.compile(r"^تعذّر الاتصال بخادم Unlimited-OCR: (.+)$", re.S),
     r"Could not connect to the Unlimited-OCR server: \1"),
    (re.compile(r"^خطأ من خادم Unlimited-OCR \((.+?)\): (.+)$", re.S),
     r"Unlimited-OCR server error (\1): \2"),
    (re.compile(r"^فشل OCR لجميع الصفحات: صفحة (\d+): (.+)$", re.S),
     r"OCR failed for all pages: page \1: \2"),
    (re.compile(r"^فشل OCR لجميع الصفحات: (.+)$", re.S),
     r"OCR failed for all pages: \1"),
    (re.compile(r"^تعذّر بناء PDF قابل للبحث: (.+)$", re.S),
     r"Could not build a searchable PDF: \1"),
    (re.compile(r"^صفحة (\d+): (.+)$", re.S), r"Page \1: \2"),
    (re.compile(r"^⏳ جارٍ استخراج النص عبر Unlimited-OCR… الصفحة (\d+)/(\d+)$"),
     r"⏳ Extracting text with Unlimited-OCR… page \1/\2"),
    (re.compile(r"^⏳ جارٍ استخراج النص عبر Unlimited-OCR… الصفحات (\d+)-(\d+)/(\d+)$"),
     r"⏳ Extracting text with Unlimited-OCR… pages \1-\2/\3"),
]


def lookup(text: str) -> str:
    """يعيد الترجمة الإنجليزية لنص عربي أو النص نفسه إن لم تُعرف ترجمته."""
    if not text:
        return text
    exact = EN_TEXT.get(text)
    if exact is not None:
        return exact
    for pattern, repl in EN_PATTERNS:
        if pattern.search(text):
            return pattern.sub(repl, text)
    return text
