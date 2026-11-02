"""
وحدة دمج عدة ملفات PDF في ملف واحد، بنفس الترتيب المُعطى.
"""

import os
from pypdf import PdfWriter


class MergeError(Exception):
    """يُرفع عند فشل عملية الدمج"""
    pass


def merge_pdfs(pdf_paths: list[str], output_path: str, progress_callback=None) -> str:
    """
    يدمج قائمة ملفات PDF بنفس ترتيبها في pdf_paths إلى ملف واحد.

    المعاملات:
        pdf_paths: قائمة مرتبة بمسارات ملفات PDF
        output_path: مسار حفظ الملف المدموج
        progress_callback: دالة اختيارية تُستدعى بـ (index, total, filename)
                            بعد إضافة كل ملف
    """
    if len(pdf_paths) < 2:
        raise MergeError("يجب اختيار ملفين على الأقل للدمج")

    for path in pdf_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"الملف غير موجود: {path}")

    writer = PdfWriter()
    total = len(pdf_paths)

    for i, path in enumerate(pdf_paths, start=1):
        try:
            writer.append(path)
        except Exception as e:
            raise MergeError(f"فشل دمج الملف '{os.path.basename(path)}': {e}") from e

        if progress_callback:
            progress_callback(i, total, os.path.basename(path))

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
