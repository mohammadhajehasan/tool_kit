"""
وحدة تنظيم صفحات PDF: تدوير، حذف، وإعادة ترتيب.
"""

import os


class OrganizeError(Exception):
    pass


def rotate_pages(
    input_path: str,
    output_path: str,
    rotations: dict[int, int],
) -> str:
    """
    يدوّر صفحات محددة.
    rotations: {page_index_0based: degrees} حيث degrees ∈ {90, 180, 270, -90}
    """
    try:
        import fitz
    except ImportError as e:
        raise OrganizeError("PyMuPDF غير مثبّت") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    doc = fitz.open(input_path)
    try:
        for idx, deg in rotations.items():
            if 0 <= idx < len(doc):
                page = doc[idx]
                page.set_rotation((page.rotation + int(deg)) % 360)
        doc.save(output_path, garbage=3, deflate=True)
    except Exception as e:
        raise OrganizeError(f"فشل تدوير الصفحات: {e}") from e
    finally:
        doc.close()
    return output_path


def delete_pages(input_path: str, output_path: str, pages_to_delete: list[int]) -> str:
    """يحذف صفحات (فهرسة من 0) ويحفظ الملف الناتج."""
    try:
        import fitz
    except ImportError as e:
        raise OrganizeError("PyMuPDF غير مثبّت") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    to_del = sorted(set(pages_to_delete), reverse=True)
    doc = fitz.open(input_path)
    try:
        if len(to_del) >= len(doc):
            raise OrganizeError("لا يمكن حذف كل الصفحات")
        for idx in to_del:
            if 0 <= idx < len(doc):
                doc.delete_page(idx)
        doc.save(output_path, garbage=4, deflate=True)
    except OrganizeError:
        raise
    except Exception as e:
        raise OrganizeError(f"فشل حذف الصفحات: {e}") from e
    finally:
        doc.close()
    return output_path


def reorder_pages(input_path: str, output_path: str, new_order: list[int]) -> str:
    """
    يعيد ترتيب الصفحات حسب new_order (فهارس من 0، يجب أن تغطي كل الصفحات مرة واحدة).
    """
    try:
        import fitz
    except ImportError as e:
        raise OrganizeError("PyMuPDF غير مثبّت") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    doc = fitz.open(input_path)
    try:
        n = len(doc)
        if sorted(new_order) != list(range(n)):
            raise OrganizeError("ترتيب الصفحات غير صالح — يجب تضمين كل الصفحات مرة واحدة")
        doc.select(new_order)
        doc.save(output_path, garbage=4, deflate=True)
    except OrganizeError:
        raise
    except Exception as e:
        raise OrganizeError(f"فشل إعادة الترتيب: {e}") from e
    finally:
        doc.close()
    return output_path


def apply_organize(
    input_path: str,
    output_path: str,
    new_order: list[int] | None = None,
    delete_indices: list[int] | None = None,
    rotations: dict[int, int] | None = None,
) -> str:
    """
    يطبّق تدوير ثم حذف ثم إعادة ترتيب في عملية واحدة على نسخة العمل.
    الترتيب الداخلي: تدوير على الفهارس الأصلية → حذف → إعادة ترتيب المتبقي.
    """
    try:
        import fitz
    except ImportError as e:
        raise OrganizeError("PyMuPDF غير مثبّت") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    doc = fitz.open(input_path)
    try:
        if rotations:
            for idx, deg in rotations.items():
                if 0 <= idx < len(doc):
                    page = doc[idx]
                    page.set_rotation((page.rotation + int(deg)) % 360)

        if delete_indices:
            for idx in sorted(set(delete_indices), reverse=True):
                if 0 <= idx < len(doc):
                    doc.delete_page(idx)
            if len(doc) == 0:
                raise OrganizeError("لا يمكن حذف كل الصفحات")

        if new_order is not None:
            # new_order بعد الحذف — فهارس نسبة للوثيقة الحالية
            if sorted(new_order) != list(range(len(doc))):
                raise OrganizeError("ترتيب الصفحات غير صالح")
            doc.select(new_order)

        doc.save(output_path, garbage=4, deflate=True)
    except OrganizeError:
        raise
    except Exception as e:
        raise OrganizeError(f"فشل تنظيم الصفحات: {e}") from e
    finally:
        doc.close()

    return output_path
