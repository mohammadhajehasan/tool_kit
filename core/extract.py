"""استخراج النصوص والصور من ملفات PDF — عبر PyMuPDF."""

import os


class ExtractError(Exception):
    pass


def extract_text(src_path: str, out_txt: str, pages: list[int] | None = None) -> dict:
    """
    يستخرج نص الصفحات إلى ملف txt بترميز UTF-8.
    pages: فهارس صفحات (من 0) — None يعني كل الصفحات.
    """
    import fitz

    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    doc = fitz.open(src_path)
    try:
        total = len(doc)
        indices = list(range(total)) if pages is None else [p for p in pages if 0 <= p < total]
        if not indices:
            raise ExtractError("لا توجد صفحات صالحة")
        parts = []
        for idx in indices:
            t = doc[idx].get_text("text").strip()
            parts.append(f"----- صفحة {idx + 1} -----\n{t}" if t else f"----- صفحة {idx + 1} -----\n(لا يوجد نص)")
    finally:
        doc.close()

    text = "\n\n".join(parts)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text)
    return {"out": out_txt, "pages": len(indices), "chars": len(text)}


def extract_images(src_path: str, out_dir: str, min_bytes: int = 1024) -> dict:
    """
    يستخرج كل الصور المضمّنة في الملف إلى مجلد (بصيغتها الأصلية وبجودتها الكاملة).
    يتجاهل الصور الصغيرة جداً (زخارف/خطوط).
    """
    import fitz

    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(src_path)
    stem = os.path.splitext(os.path.basename(src_path))[0]
    seen, count = set(), 0
    try:
        for pno in range(len(doc)):
            for img in doc[pno].get_images(full=True):
                xref = img[0]
                if xref in seen:
                    continue
                seen.add(xref)
                try:
                    info = doc.extract_image(xref)
                except Exception:
                    continue
                data = info.get("image", b"")
                if len(data) < min_bytes:
                    continue
                count += 1
                out = os.path.join(out_dir, f"{stem}_صورة_{count:03d}.{info.get('ext', 'png')}")
                with open(out, "wb") as f:
                    f.write(data)
    finally:
        doc.close()
    return {"count": count, "dir": out_dir}
