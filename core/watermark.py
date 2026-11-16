"""
وحدة إضافة علامة مائية نصية أو صورة على صفحات PDF.
"""

import os


class WatermarkError(Exception):
    pass


def _arabic_fontfile() -> str | None:
    """يبحث عن خط يدعم العربية على ويندوز/لينكس إن وُجد."""
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\segoui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def add_text_watermark(
    input_path: str,
    output_path: str,
    text: str,
    opacity: float = 0.25,
    angle: float = 45.0,
    font_size: float = 48.0,
    color: tuple[float, float, float] = (0.5, 0.5, 0.5),
    pages: list[int] | None = None,
    progress_callback=None,
    cancel_check=None,
) -> str:
    """يضع علامة مائية نصية مائلة في منتصف كل صفحة محددة."""
    try:
        import fitz
    except ImportError as e:
        raise WatermarkError("PyMuPDF غير مثبّت. ثبّته: pip install pymupdf") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")
    if not text.strip():
        raise WatermarkError("نص العلامة المائية فارغ")

    opacity = max(0.05, min(1.0, float(opacity)))
    fontfile = _arabic_fontfile()

    doc = fitz.open(input_path)
    try:
        indices = pages if pages is not None else list(range(len(doc)))
        total = len(indices) or 1
        for i, page_idx in enumerate(indices):
            if cancel_check and cancel_check():
                raise WatermarkError("تم إلغاء العملية")
            if page_idx < 0 or page_idx >= len(doc):
                continue
            page = doc[page_idx]
            rect = page.rect
            cx, cy = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
            # تقدير عرض النص تقريباً لتمركز أفضل
            approx_w = font_size * max(len(text), 1) * 0.45
            start = fitz.Point(cx - approx_w / 2, cy)
            morph = (fitz.Point(cx, cy), fitz.Matrix(angle))
            kwargs = dict(
                fontsize=font_size,
                color=color,
                fill_opacity=opacity,
                render_mode=0,
                morph=morph,
                overlay=True,
            )
            if fontfile:
                kwargs["fontfile"] = fontfile
            try:
                page.insert_text(start, text, **kwargs)
            except Exception:
                box_kwargs = dict(
                    fontsize=font_size,
                    color=color,
                    align=fitz.TEXT_ALIGN_CENTER,
                    overlay=True,
                    fill_opacity=opacity,
                )
                if fontfile:
                    box_kwargs["fontfile"] = fontfile
                page.insert_textbox(rect, text, **box_kwargs)
            if progress_callback:
                progress_callback(i + 1, total, f"صفحة {page_idx + 1}")
        doc.save(output_path, garbage=3, deflate=True)
    except WatermarkError:
        raise
    except Exception as e:
        raise WatermarkError(f"فشل إضافة العلامة المائية: {e}") from e
    finally:
        doc.close()

    return output_path


def add_image_watermark(
    input_path: str,
    output_path: str,
    image_path: str,
    opacity: float = 0.3,
    scale: float = 0.35,
    pages: list[int] | None = None,
    progress_callback=None,
    cancel_check=None,
) -> str:
    """يضع صورة/شعار كعلامة مائية في منتصف الصفحات."""
    try:
        import fitz
    except ImportError as e:
        raise WatermarkError("PyMuPDF غير مثبّت. ثبّته: pip install pymupdf") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"صورة العلامة غير موجودة: {image_path}")

    opacity = max(0.05, min(1.0, float(opacity)))
    scale = max(0.05, min(1.0, float(scale)))

    doc = fitz.open(input_path)
    try:
        indices = pages if pages is not None else list(range(len(doc)))
        total = len(indices) or 1
        for i, page_idx in enumerate(indices):
            if cancel_check and cancel_check():
                raise WatermarkError("تم إلغاء العملية")
            if page_idx < 0 or page_idx >= len(doc):
                continue
            page = doc[page_idx]
            rect = page.rect
            side = min(rect.width, rect.height) * scale
            x0 = (rect.width - side) / 2
            y0 = (rect.height - side) / 2
            img_rect = fitz.Rect(x0, y0, x0 + side, y0 + side)
            page.insert_image(img_rect, filename=image_path, overlay=True, opacity=opacity)
            if progress_callback:
                progress_callback(i + 1, total, f"صفحة {page_idx + 1}")
        doc.save(output_path, garbage=3, deflate=True)
    except WatermarkError:
        raise
    except Exception as e:
        raise WatermarkError(f"فشل إضافة صورة العلامة: {e}") from e
    finally:
        doc.close()

    return output_path
