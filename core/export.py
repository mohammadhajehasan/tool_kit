"""
تصدير محتوى PDF إلى Word (.docx) و Excel (.xlsx).
"""

import os
from pathlib import Path


class ExportError(Exception):
    pass


def pdf_to_docx(
    input_path: str,
    output_path: str,
    progress_callback=None,
    cancel_check=None,
) -> str:
    """يحوّل PDF إلى مستند Word عبر pdf2docx."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    try:
        from pdf2docx import Converter
    except ImportError as e:
        raise ExportError("ثبّت pdf2docx: pip install pdf2docx") from e

    if cancel_check and cancel_check():
        raise ExportError("تم إلغاء العملية")

    if progress_callback:
        progress_callback(1, 2, "تحويل إلى Word…")

    cv = Converter(input_path)
    try:
        cv.convert(output_path)
    except Exception as e:
        raise ExportError(f"فشل التحويل إلى Word: {e}") from e
    finally:
        cv.close()

    if progress_callback:
        progress_callback(2, 2, "اكتمل")
    if cancel_check and cancel_check():
        raise ExportError("تم إلغاء العملية")
    return output_path


def pdf_to_excel(
    input_path: str,
    output_path: str,
    progress_callback=None,
    cancel_check=None,
) -> dict:
    """
    يستخرج الجداول من PDF إلى ملف Excel (ورقة لكل جدول).
    إن لم تُوجد جداول، يصدّر النص سطراً بسطر في ورقة واحدة.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    try:
        import pdfplumber
        from openpyxl import Workbook
    except ImportError as e:
        raise ExportError("ثبّت pdfplumber و openpyxl: pip install pdfplumber openpyxl") from e

    wb = Workbook()
    # احذف الورقة الافتراضية لاحقاً إن أضفنا غيرها
    default_sheet = wb.active
    default_sheet.title = "نص"
    tables_count = 0
    text_rows = []

    with pdfplumber.open(input_path) as pdf:
        total = len(pdf.pages) or 1
        for i, page in enumerate(pdf.pages):
            if cancel_check and cancel_check():
                raise ExportError("تم إلغاء العملية")
            tables = page.extract_tables() or []
            for t_idx, table in enumerate(tables):
                if not table:
                    continue
                tables_count += 1
                ws = wb.create_sheet(title=f"جدول_{tables_count}"[:31])
                for r_idx, row in enumerate(table, start=1):
                    for c_idx, cell in enumerate(row or [], start=1):
                        ws.cell(row=r_idx, column=c_idx, value=cell if cell is not None else "")
            # اجمع النص كنسخة احتياطية
            txt = page.extract_text() or ""
            for line in txt.splitlines():
                if line.strip():
                    text_rows.append(line)
            if progress_callback:
                progress_callback(i + 1, total, f"صفحة {i + 1}")

    if tables_count > 0:
        # احذف ورقة النص إن وُجدت جداول
        if "نص" in wb.sheetnames and len(wb.sheetnames) > 1:
            wb.remove(wb["نص"])
    else:
        for r, line in enumerate(text_rows, start=1):
            default_sheet.cell(row=r, column=1, value=line)
        if not text_rows:
            default_sheet.cell(row=1, column=1, value="لم يُعثر على جداول أو نص قابل للاستخراج")

    try:
        wb.save(output_path)
    except Exception as e:
        raise ExportError(f"فشل حفظ Excel: {e}") from e

    return {"output": output_path, "tables": tables_count, "text_rows": len(text_rows)}


def extract_plain_text(input_path: str) -> str:
    """يستخرج النص المضمّن من PDF (بدون OCR)."""
    try:
        import fitz
    except ImportError as e:
        raise ExportError("PyMuPDF غير مثبّت") from e
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")
    doc = fitz.open(input_path)
    try:
        return "\n\n".join((page.get_text("text") or "").strip() for page in doc)
    finally:
        doc.close()
