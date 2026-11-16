"""
محرك OCR عربي/إنجليزي للمستندات الممسوحة.
يعتمد على Tesseract عبر pytesseract + PyMuPDF لبناء طبقة نص قابلة للبحث.
"""

import os
import shutil
from pathlib import Path


class OcrError(Exception):
    pass


def tesseract_available() -> tuple[bool, str]:
    """يرجع (متاح؟, مسار أو رسالة)."""
    try:
        import pytesseract
    except ImportError:
        return False, "ثبّت pytesseract: pip install pytesseract"

    exe = shutil.which("tesseract")
    if not exe and os.name == "nt":
        for candidate in (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ):
            if os.path.isfile(candidate):
                exe = candidate
                break
    if not exe:
        return False, (
            "Tesseract غير مثبّت.\n"
            "حمّله من: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "وتأكد من تثبيت حزمة اللغة العربية (ara)."
        )
    try:
        pytesseract.pytesseract.tesseract_cmd = exe
        _ = pytesseract.get_tesseract_version()
    except Exception as e:
        return False, f"تعذّر تشغيل Tesseract: {e}"
    return True, exe


def ocr_pdf(
    input_path: str,
    output_path: str,
    lang: str = "ara+eng",
    dpi: int = 200,
    progress_callback=None,
    cancel_check=None,
) -> dict:
    """
    يحوّل PDF ممسوحاً إلى PDF قابل للبحث (طبقة نص غير مرئية فوق الصور).

    يرجع: {output, pages, lang, engine}
    """
    try:
        import fitz
        import pytesseract
        from PIL import Image
        import io
    except ImportError as e:
        raise OcrError(f"مكتبة ناقصة: {e}") from e

    ok, info = tesseract_available()
    if not ok:
        raise OcrError(info)
    pytesseract.pytesseract.tesseract_cmd = info

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    src = fitz.open(input_path)
    out = fitz.open()
    try:
        total = len(src) or 1
        for i in range(len(src)):
            if cancel_check and cancel_check():
                raise OcrError("تم إلغاء العملية")
            page = src[i]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            try:
                data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
            except pytesseract.TesseractError as e:
                raise OcrError(
                    f"فشل OCR (تحقق من تثبيت لغة {lang}): {e}"
                ) from e

            # صفحة جديدة بنفس مقاس الأصلية مع صورة الخلفية
            new_page = out.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, pixmap=pix)

            # طبقة نص شفافة حسب صناديق الكلمات
            scale = page.rect.width / pix.width if pix.width else 1.0
            n = len(data.get("text", []))
            for j in range(n):
                word = (data["text"][j] or "").strip()
                conf = int(float(data["conf"][j])) if str(data["conf"][j]).lstrip("-").isdigit() else -1
                if not word or conf < 0:
                    continue
                x, y, w, h = data["left"][j], data["top"][j], data["width"][j], data["height"][j]
                rect = fitz.Rect(x * scale, y * scale, (x + w) * scale, (y + h) * scale)
                # نص غير مرئي قابل للنسخ/البحث
                try:
                    new_page.insert_textbox(
                        rect,
                        word,
                        fontsize=max(6, rect.height * 0.8),
                        color=(0, 0, 0),
                        fill_opacity=0.01,
                        overlay=True,
                        align=fitz.TEXT_ALIGN_CENTER,
                    )
                except Exception:
                    continue

            if progress_callback:
                progress_callback(i + 1, total, f"صفحة {i + 1}")

        out.save(output_path, garbage=3, deflate=True)
    finally:
        out.close()
        src.close()

    return {"output": output_path, "pages": total, "lang": lang, "engine": "tesseract"}


def extract_text_ocr(
    input_path: str,
    lang: str = "ara+eng",
    dpi: int = 200,
    progress_callback=None,
    cancel_check=None,
) -> str:
    """يستخرج نصاً عبر OCR دون حفظ PDF جديد."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise OcrError(f"مكتبة ناقصة: {e}") from e

    ok, info = tesseract_available()
    if not ok:
        raise OcrError(info)
    pytesseract.pytesseract.tesseract_cmd = info

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    parts = []
    doc = fitz.open(input_path)
    try:
        total = len(doc) or 1
        for i in range(len(doc)):
            if cancel_check and cancel_check():
                raise OcrError("تم إلغاء العملية")
            pix = doc[i].get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang=lang)
            parts.append(text.strip())
            if progress_callback:
                progress_callback(i + 1, total, f"صفحة {i + 1}")
    finally:
        doc.close()
    return "\n\n".join(parts)
