"""
وحدة تقطيع ملفات PDF
تدعم استخراج صفحات محددة إلى ملف واحد، أو تقسيم كل صفحة إلى ملف مستقل،
أو تقسيم الملف إلى مجموعات حسب نطاقات صفحات.
"""

import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter


class SplitError(Exception):
    """يُرفع عند فشل عملية التقطيع"""
    pass


def get_page_count(input_path: str) -> int:
    """يرجع عدد صفحات ملف PDF"""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")
    reader = PdfReader(input_path)
    return len(reader.pages)


def parse_page_ranges(ranges_str: str, total_pages: int) -> list[int]:
    """
    يحول نص نطاقات الصفحات مثل "1-3,5,8-10" إلى قائمة أرقام صفحات
    (فهرسة تبدأ من 0 داخلياً، لكن المستخدم يُدخل الأرقام بدءاً من 1).
    """
    pages = set()
    ranges_str = ranges_str.replace(" ", "")
    if not ranges_str:
        raise SplitError("لم يتم تحديد أي صفحات")

    for part in ranges_str.split(","):
        if "-" in part:
            try:
                start, end = part.split("-")
                start, end = int(start), int(end)
            except ValueError:
                raise SplitError(f"صيغة نطاق غير صحيحة: {part}")
            if start < 1 or end > total_pages or start > end:
                raise SplitError(f"نطاق خارج حدود الملف: {part} (عدد الصفحات: {total_pages})")
            pages.update(range(start - 1, end))
        else:
            try:
                p = int(part)
            except ValueError:
                raise SplitError(f"رقم صفحة غير صحيح: {part}")
            if p < 1 or p > total_pages:
                raise SplitError(f"رقم صفحة خارج الحدود: {p} (عدد الصفحات: {total_pages})")
            pages.add(p - 1)

    return sorted(pages)


def extract_pages(input_path: str, pages: list[int], output_path: str) -> str:
    """
    يستخرج مجموعة صفحات محددة (فهرسة من 0) إلى ملف PDF واحد جديد.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for p in pages:
        if p < 0 or p >= len(reader.pages):
            raise SplitError(f"رقم صفحة غير صالح: {p + 1}")
        writer.add_page(reader.pages[p])

    if len(writer.pages) == 0:
        raise SplitError("لم يتم تحديد أي صفحات صالحة للاستخراج")

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def split_to_individual_files(input_path: str, output_dir: str, pages: list[int] = None) -> list[str]:
    """
    يقسم كل صفحة (أو الصفحات المحددة فقط) إلى ملف PDF مستقل.
    يرجع قائمة بمسارات الملفات الناتجة.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(input_path)
    base_name = Path(input_path).stem

    target_pages = pages if pages is not None else range(len(reader.pages))

    output_files = []
    for p in target_pages:
        if p < 0 or p >= len(reader.pages):
            continue
        writer = PdfWriter()
        writer.add_page(reader.pages[p])
        out_path = os.path.join(output_dir, f"{base_name}_صفحة_{p + 1}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append(out_path)

    return output_files


def render_page_thumbnails(input_path: str, max_width: int = 160) -> list:
    """
    يرسم معاينة مصغّرة (thumbnail) لكل صفحة من ملف PDF ويعيد قائمة بكائنات PIL.Image.

    يستخدم PyMuPDF (fitz) لعرض سريع وعالي الجودة.

    المعاملات:
        input_path: مسار ملف PDF
        max_width: أقصى عرض للصورة المصغّرة (بالبكسل)

    يرجع:
        list من كائنات PIL.Image (صورة لكل صفحة).
        إذا فشل الرسم لصفحة معيّنة، يُضاف None مكانها.
    """
    import fitz  # PyMuPDF (موجود في المتطلبات)

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    images = []
    doc = fitz.open(input_path)
    try:
        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                # تحديد ارتفاع يتناسب مع العرض المطلوب
                rect = page.rect
                zoom = max_width / rect.width
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                # تحويل pixmap إلى PIL.Image
                from PIL import Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            except Exception:
                images.append(None)
    finally:
        doc.close()

    return images
