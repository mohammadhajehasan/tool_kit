"""إعادة ترتيب / تدوير / حذف صفحات PDF عبر PyMuPDF."""

import os


class PagesError(Exception):
    pass


def rotate_value(current_deg: int) -> int:
    """يضيف 90 درجة لقيمة التدوير (0/90/180/270)."""
    return (current_deg + 90) % 360


def organize(
    src_path: str,
    output_path: str,
    order: list[int],
    rotations: dict[int, int] | None = None,
) -> str:
    """
    يبني PDF جديداً بالصفحات والترتيب المطلوب.
    order: فهارس الصفحات (من 0) بالترتيب الجديد المطلوب.
    rotations: {فهرس أصلي: زاوية 0/90/180/270}.
    """
    import fitz

    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")
    if not order:
        raise PagesError("لا توجد صفحات للحفظ — احذف التطبيق من إزالة كل الصفحات")

    doc = fitz.open(src_path)
    try:
        total = len(doc)
        if any(i < 0 or i >= total for i in order):
            raise PagesError("فهرس صفحة غير صالح")
        rotations = rotations or {}
        for idx, rot in rotations.items():
            if 0 <= idx < total and rot % 360:
                doc[idx].set_rotation(rot % 360)
        doc.select(list(order))
        doc.save(output_path, garbage=3, deflate=True)
    finally:
        doc.close()
    return output_path
