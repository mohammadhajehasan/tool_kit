"""OCR (التعرف الضوئي على الحروف) — يتطلب Tesseract وpytesseract (اختياري).

ينتج PDF قابلاً للبحث والنسخ من صفحات ممسوحة ضوئياً.
"""

import io
import os


class OcrError(Exception):
    pass


INSTALL_HINT = (
    "لتفعيل OCR:\n"
    "1) ثبّت Tesseract OCR من: https://github.com/UB-Mannheim/tesseract/wiki\n"
    "2) أثناء التثبيت اختر حزمة اللغة العربية (Arabic) والإنجليزية\n"
    "3) ثبّت مكتبة بايثون: pip install pytesseract\n"
    "4) إذا لم يُعثر على tesseract.exe أضف مساره إلى متغير PATH"
)


def available() -> bool:
    """هل OCR جاهز على هذا النظام؟"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def ocr_pdf(src_path: str, output_path: str, lang: str = "ara+eng",
            dpi: int = 200, cancel_check=None) -> dict:
    """
    يبني PDF قابلاً للبحث: كل صفحة تُمسح ضوئياً ثم تُضاف طبقة نص مخفي.
    lang: صيغة Tesseract مثل "ara+eng".
    """
    try:
        import fitz
        import pytesseract
        from PIL import Image
        from pypdf import PdfWriter
    except ImportError as e:
        raise OcrError(f"مكتبة ناقصة: {e}\n\n{INSTALL_HINT}")

    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    doc = fitz.open(src_path)
    writer = PdfWriter()
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pages = 0
    try:
        for idx in range(len(doc)):
            if cancel_check and cancel_check():
                raise InterruptedError("تم إلغاء العملية")
            pix = doc[idx].get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            try:
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension="pdf")
            except pytesseract.TesseractError as e:
                raise OcrError(
                    f"فشل التعرف على النص (اللغة: {lang}).\n{e}\n\n"
                    "تأكد من تثبيت حزم اللغات (ara / eng) في Tesseract."
                )
            writer.append(io.BytesIO(pdf_bytes))
            pages += 1
    finally:
        doc.close()

    if pages == 0:
        raise OcrError("لا توجد صفحات للمعالجة")

    with open(output_path, "wb") as f:
        writer.write(f)
    return {"out": output_path, "pages": pages, "lang": lang}
