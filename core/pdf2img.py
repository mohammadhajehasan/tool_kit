"""تحويل صفحات PDF إلى صور JPG/PNG عبر PyMuPDF."""

import os
from pathlib import Path


class Pdf2ImgError(Exception):
    pass


def pdf_to_images(
    input_path: str,
    output_dir: str,
    fmt: str = "jpg",
    dpi: int = 150,
    quality: int = 85,
    pages: list[int] | None = None,
    prefix: str | None = None,
    cancel_check=None,
) -> list[str]:
    """
    يحوّل صفحات PDF إلى صور.
    pages: قائمة فهارس صفحات (من 0) — None يعني كل الصفحات.
    يرجع قائمة مسارات الصور الناتجة.
    """
    import fitz

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    doc = fitz.open(input_path)
    total = len(doc)
    if pages is None:
        indices = list(range(total))
    else:
        indices = [p for p in pages if 0 <= p < total]
    if not indices:
        doc.close()
        raise Pdf2ImgError("لا توجد صفحات صالحة للتحويل")

    os.makedirs(output_dir, exist_ok=True)
    base = prefix or Path(input_path).stem
    ext = "jpg" if fmt.lower() in ("jpg", "jpeg") else fmt.lower()
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    outputs = []
    try:
        for idx in indices:
            if cancel_check and cancel_check():
                raise InterruptedError("تم إلغاء العملية")
            pix = doc[idx].get_pixmap(matrix=mat, alpha=False)
            out_path = os.path.join(output_dir, f"{base}_صفحة_{idx + 1}.{ext}")
            if ext == "jpg":
                try:
                    pix.save(out_path, jpg_quality=quality)
                except TypeError:
                    pix.pil_save(out_path, quality=quality)
            else:
                pix.save(out_path)
            outputs.append(out_path)
    finally:
        doc.close()

    return outputs
