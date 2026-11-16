"""
مقارنة نسختين من PDF — فروقات نصية على مستوى الكلمات/الأسطر.
"""

import difflib
import os
from dataclasses import dataclass


class DiffError(Exception):
    pass


@dataclass
class DiffResult:
    html: str
    added: int
    removed: int
    pages_a: int
    pages_b: int


def _page_texts(path: str) -> list[str]:
    try:
        import fitz
    except ImportError as e:
        raise DiffError("PyMuPDF غير مثبّت") from e
    if not os.path.isfile(path):
        raise FileNotFoundError(f"الملف غير موجود: {path}")
    doc = fitz.open(path)
    try:
        return [(p.get_text("text") or "") for p in doc]
    finally:
        doc.close()


def compare_pdfs(
    path_a: str,
    path_b: str,
    progress_callback=None,
    cancel_check=None,
) -> DiffResult:
    """
    يقارن نص الملفين ويعيد HTML ملوّناً (أخضر=إضافة، أحمر=حذف).
    """
    texts_a = _page_texts(path_a)
    if progress_callback:
        progress_callback(1, 3, "قراءة الملف الأول…")
    texts_b = _page_texts(path_b)
    if progress_callback:
        progress_callback(2, 3, "قراءة الملف الثاني…")
    if cancel_check and cancel_check():
        raise DiffError("تم إلغاء العملية")

    # وحّد النص بأسطر مع وسم رقم الصفحة
    def flatten(pages: list[str]) -> list[str]:
        lines = []
        for i, t in enumerate(pages):
            lines.append(f"—— صفحة {i + 1} ——")
            for line in (t or "").splitlines():
                lines.append(line)
            lines.append("")
        return lines

    a_lines = flatten(texts_a)
    b_lines = flatten(texts_b)

    matcher = difflib.SequenceMatcher(None, a_lines, b_lines)
    html_parts = [
        "<html><head><meta charset='utf-8'></head>",
        "<body style='font-family:Segoe UI,Tahoma,sans-serif;direction:rtl;"
        "font-size:13px;line-height:1.6;padding:12px;'>",
        "<h3>نتيجة المقارنة</h3>",
    ]
    added = removed = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in a_lines[i1:i2]:
                html_parts.append(f"<div>{_esc(line)}</div>")
        elif tag == "delete":
            for line in a_lines[i1:i2]:
                removed += 1
                html_parts.append(
                    f"<div style='background:#FEE2E2;color:#991B1B;"
                    f"text-decoration:line-through;padding:2px 6px;border-radius:4px;'>"
                    f"− {_esc(line)}</div>"
                )
        elif tag == "insert":
            for line in b_lines[j1:j2]:
                added += 1
                html_parts.append(
                    f"<div style='background:#DCFCE7;color:#166534;"
                    f"padding:2px 6px;border-radius:4px;'>"
                    f"+ {_esc(line)}</div>"
                )
        elif tag == "replace":
            for line in a_lines[i1:i2]:
                removed += 1
                html_parts.append(
                    f"<div style='background:#FEE2E2;color:#991B1B;"
                    f"text-decoration:line-through;padding:2px 6px;border-radius:4px;'>"
                    f"− {_esc(line)}</div>"
                )
            for line in b_lines[j1:j2]:
                added += 1
                html_parts.append(
                    f"<div style='background:#DCFCE7;color:#166534;"
                    f"padding:2px 6px;border-radius:4px;'>"
                    f"+ {_esc(line)}</div>"
                )

    html_parts.append("</body></html>")
    if progress_callback:
        progress_callback(3, 3, "اكتمل")

    return DiffResult(
        html="\n".join(html_parts),
        added=added,
        removed=removed,
        pages_a=len(texts_a),
        pages_b=len(texts_b),
    )


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
