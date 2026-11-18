"""إصلاح ملفات PDF التالفة — pikepdf ثم PyMuPDF كاحتياط."""

import os


class RepairError(Exception):
    pass


def repair(src_path: str, output_path: str) -> dict:
    """
    يحاول فتح الملف وإعادة حفظه سليماً.
    pikepdf يصلح تلقائياً أغلب التلف الشائع (جداول xref مكسورة، كائنات ناقصة).
    """
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    note = ""
    try:
        import pikepdf
        with pikepdf.open(src_path, attempt_recovery=True) as pdf:
            pdf.save(output_path, linearize=True)
        note = "pikepdf"
    except Exception as e1:
        try:
            import fitz
            doc = fitz.open(src_path)
            doc.save(output_path, garbage=3, deflate=True)
            doc.close()
            note = "PyMuPDF"
        except Exception as e2:
            raise RepairError(f"تعذر إصلاح الملف.\npikepdf: {e1}\nPyMuPDF: {e2}")

    if not os.path.isfile(output_path) or os.path.getsize(output_path) < 100:
        raise RepairError("لم ينتج ملف صالح — الملف قد يكون تالفاً بشكل غير قابل للإصلاح")

    return {"out": output_path, "engine": note, "size": os.path.getsize(output_path)}
