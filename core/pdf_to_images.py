"""
وحدة تحويل صفحات PDF إلى صور (PNG / JPEG).
"""

import os
from pathlib import Path


class PdfToImagesError(Exception):
    pass


SUPPORTED_FORMATS = {"png", "jpg", "jpeg"}


def pdf_to_images(
    input_path: str,
    output_dir: str,
    dpi: int = 150,
    fmt: str = "png",
    pages: list[int] | None = None,
    progress_callback=None,
    cancel_check=None,
) -> list[str]:
    """
    يصدّر صفحات PDF كصور منفصلة.

    pages: فهارس من 0، أو None لكل الصفحات
    cancel_check: دالة ترجع True عند طلب الإلغاء
    """
    try:
        import fitz
    except ImportError as e:
        raise PdfToImagesError("PyMuPDF غير مثبّت. ثبّته: pip install pymupdf") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    fmt = fmt.lower().replace("jpeg", "jpg")
    if fmt not in SUPPORTED_FORMATS:
        raise PdfToImagesError(f"صيغة غير مدعومة: {fmt}")

    os.makedirs(output_dir, exist_ok=True)
    stem = Path(input_path).stem
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    outputs: list[str] = []

    doc = fitz.open(input_path)
    try:
        indices = pages if pages is not None else list(range(len(doc)))
        total = len(indices) or 1
        for i, page_idx in enumerate(indices):
            if cancel_check and cancel_check():
                raise PdfToImagesError("تم إلغاء العملية")
            if page_idx < 0 or page_idx >= len(doc):
                continue
            page = doc.load_page(page_idx)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out_name = f"{stem}_صفحة_{page_idx + 1}.{fmt}"
            out_path = os.path.join(output_dir, out_name)
            if fmt == "png":
                pix.save(out_path)
            else:
                pix.save(out_path, output="jpeg", jpg_quality=90)
            outputs.append(out_path)
            if progress_callback:
                progress_callback(i + 1, total, out_name)
    finally:
        doc.close()

    if not outputs:
        raise PdfToImagesError("لم يتم تصدير أي صفحة")
    return outputs
