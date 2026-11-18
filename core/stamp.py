"""علامة مائية (نص/صورة) وترقيم صفحات — عبر PyMuPDF.

دعم العربية: عبر insert_htmlbox الذي يتعامل مع تشكيل الحروف واتجاه RTL.
"""

import os


class StampError(Exception):
    pass


_GRAY = (0.55, 0.55, 0.55)


def _arabic_font_path() -> str | None:
    """يبحث عن خط يدعم العربية في مجلد خطوط ويندوز."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    for name in ("arial.ttf", "segoeui.ttf", "tahoma.ttf", "calibri.ttf"):
        p = os.path.join(windir, "Fonts", name)
        if os.path.isfile(p):
            return p
    return None


def _make_text_stamp(text, opacity, fontsize, color, width_hint: int = 0) -> "object":
    """
    يبني PDF مؤقتاً من صفحة واحدة تحوي نص العلامة المائية (بالشفافية واللون المطلوبين).
    ختمه لاحقاً بـ show_pdf_page داخل مربّع يسمح بأي زاوية دون تصغير.
    """
    import fitz

    font_path = _arabic_font_path()
    archive = None
    family = "sans-serif"
    css = ""
    if font_path:
        archive = fitz.Archive(os.path.dirname(font_path))
        family = "wt-font"
        css = "@font-face {font-family: wt-font; src: url('%s');}" % os.path.basename(font_path)

    rgb = color or _GRAY
    hexc = "#%02x%02x%02x" % tuple(int(c * 255) for c in rgb)

    width = max(int(width_hint), int(fontsize * len(text) * 1.2) + 200)
    height = int(fontsize * 2.2)
    html = (
        f"<div style=\"font-family:{family}; color:{hexc}; "
        f"font-size:{int(fontsize)}px; text-align:center;\">{text}</div>"
    )

    stamp = fitz.open()
    page = stamp.new_page(width=width, height=height)
    rect = page.rect
    import inspect
    sig = inspect.signature(page.insert_htmlbox)
    kwargs = {}
    for name, val in (("css", css), ("opacity", opacity), ("archive", archive)):
        if name in sig.parameters:
            kwargs[name] = val
    try:
        page.insert_htmlbox(rect, html, **kwargs)
    except Exception:
        page.insert_textbox(
            rect, text, fontname="helv", fontsize=fontsize, color=rgb,
            align=fitz.TEXT_ALIGN_CENTER,
        )
    return stamp


def _insert_text_watermark(page, text, opacity, angle, fontsize, color):
    """يختم نص العلامة المائية في منتصف الصفحة بالزاوية المطلوبة (يدعم العربية)."""
    import fitz

    rect = page.rect
    cx, cy = rect.width / 2, rect.height / 2
    diag = (rect.width ** 2 + rect.height ** 2) ** 0.5 + 60

    stamp = _make_text_stamp(text, opacity, fontsize, color, width_hint=int(diag))
    try:
        h = stamp[0].rect.height
        # مربّع بحجم القطر: أي دوران يبقى داخل الحدود دون تصغير تلقائي
        square = fitz.Rect(cx - diag / 2, cy - diag / 2, cx + diag / 2, cy + diag / 2)
        page.show_pdf_page(square, stamp, 0, rotate=angle % 360, overlay=True)
    finally:
        stamp.close()


def watermark(
    src_path: str,
    output_path: str,
    text: str | None = None,
    image_path: str | None = None,
    opacity: float = 0.30,
    angle: int = 30,
    fontsize: int = 48,
    color=None,
    cancel_check=None,
) -> str:
    """يطبّق علامة مائية نصية و/أو صورة على كل الصفحات."""
    import fitz

    if not text and not image_path:
        raise StampError("أدخل نص العلامة المائية أو اختر صورة")
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    doc = fitz.open(src_path)
    try:
        for idx in range(len(doc)):
            if cancel_check and cancel_check():
                raise InterruptedError("تم إلغاء العملية")
            page = doc[idx]
            if image_path:
                if not os.path.isfile(image_path):
                    raise StampError(f"صورة العلامة المائية غير موجودة: {image_path}")
                try:
                    from PIL import Image
                    img = Image.open(image_path).convert("RGBA")
                    if 0 < opacity < 1:
                        alpha = img.split()[3].point(lambda a: int(a * opacity))
                        img.putalpha(alpha)
                        import tempfile
                        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                        tmp.close()
                        img.save(tmp.name)
                        page.insert_image(page.rect, filename=tmp.name,
                                          overlay=True, keep_proportion=True)
                        os.unlink(tmp.name)
                    else:
                        page.insert_image(page.rect, filename=image_path,
                                          overlay=True, keep_proportion=True)
                except ImportError:
                    page.insert_image(page.rect, filename=image_path,
                                      overlay=True, keep_proportion=True)
            if text:
                _insert_text_watermark(page, text, opacity, angle, fontsize, color)
        doc.save(output_path, garbage=3, deflate=True)
    finally:
        doc.close()
    return output_path


def add_page_numbers(
    src_path: str,
    output_path: str,
    mode: str = "page_of_ar",
    position: str = "bottom-center",
    start: int = 1,
    fontsize: int = 10,
    cancel_check=None,
) -> str:
    """
    يرقّم الصفحات.
    mode: "x" | "dash" | "page_of_en" | "page_of_ar"
    position: bottom-center | bottom-left | bottom-right | top-center
    """
    import fitz

    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    doc = fitz.open(src_path)
    try:
        total = len(doc)
        for idx in range(total):
            if cancel_check and cancel_check():
                raise InterruptedError("تم إلغاء العملية")
            page = doc[idx]
            n = start + idx
            if mode == "x":
                page.insert_textbox(
                    fitz.Rect(0, page.rect.height - 26, page.rect.width, page.rect.height - 6),
                    str(n), fontname="helv", fontsize=fontsize, color=_GRAY,
                    align=fitz.TEXT_ALIGN_CENTER,
                )
                continue

            if mode == "dash":
                text = f"- {n} -"
            elif mode == "page_of_en":
                text = f"Page {n} of {total}"
            else:
                text = f"صفحة {n} من {total}"

            h, w = page.rect.height, page.rect.width
            if position == "top-center":
                rect = fitz.Rect(0, 6, w, 26)
            elif position == "bottom-left":
                rect = fitz.Rect(24, h - 26, w * 0.5, h - 6)
            elif position == "bottom-right":
                rect = fitz.Rect(w * 0.5, h - 26, w - 24, h - 6)
            else:
                rect = fitz.Rect(0, h - 26, w, h - 6)

            if mode == "page_of_ar":
                font_path = _arabic_font_path()
                archive = None
                css = ""
                if font_path:
                    archive = fitz.Archive(os.path.dirname(font_path))
                    css = "@font-face {font-family: wt-font; src: url('%s');}" % os.path.basename(font_path)
                    html = (f"<div style='font-family:wt-font; color:rgb(140,140,140); "
                            f"font-size:{fontsize}px; text-align:center;'>{text}</div>")
                else:
                    html = (f"<div style='font-family:sans-serif; color:rgb(140,140,140); "
                            f"font-size:{fontsize}px; text-align:center;'>{text}</div>")
                import inspect
                sig = inspect.signature(page.insert_htmlbox)
                kwargs = {}
                for name, val in (("css", css), ("archive", archive)):
                    if name in sig.parameters:
                        kwargs[name] = val
                try:
                    page.insert_htmlbox(rect, html, **kwargs)
                except Exception:
                    page.insert_textbox(rect, f"Page {n} of {total}",
                                        fontname="helv", fontsize=fontsize,
                                        color=_GRAY, align=fitz.TEXT_ALIGN_CENTER)
            else:
                page.insert_textbox(
                    rect, text, fontname="helv", fontsize=fontsize,
                    color=_GRAY, align=fitz.TEXT_ALIGN_CENTER,
                )
        doc.save(output_path, garbage=3, deflate=True)
    finally:
        doc.close()
    return output_path
