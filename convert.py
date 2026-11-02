"""
وحدة تحويل صورة أو مجموعة صور (بمختلف الصيغ) إلى ملف PDF واحد.
تدعم: JPG, JPEG, PNG, BMP, TIFF, WEBP, GIF (أول إطار)
"""

import os
import img2pdf
from PIL import Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".gif"}


class ConvertError(Exception):
    """يُرفع عند فشل عملية التحويل"""
    pass


def is_supported_image(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS


def _normalize_image(path: str, tmp_dir: str) -> str:
    """
    يحول الصورة إلى JPEG قياسي (RGB، بدون قناة شفافية) لضمان توافقها مع img2pdf،
    خصوصاً لصيغ مثل PNG الشفافة أو WEBP أو GIF المتحركة.
    يرجع مسار النسخة المُعالجة، أو المسار الأصلي إذا لم تكن هناك حاجة للتحويل.
    """
    ext = os.path.splitext(path)[1].lower()

    # img2pdf يدعم JPEG وPNG (بدون شفافية) مباشرة بدون إعادة ترميز
    if ext in {".jpg", ".jpeg"}:
        return path

    try:
        with Image.open(path) as img:
            if ext == ".gif":
                img.seek(0)  # أول إطار فقط للصور المتحركة

            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                img_converted = img.convert("RGBA") if img.mode != "RGBA" else img
                background.paste(img_converted, mask=img_converted.split()[-1] if img_converted.mode == "RGBA" else None)
                img_final = background
            else:
                img_final = img.convert("RGB")

            out_path = os.path.join(
                tmp_dir, os.path.splitext(os.path.basename(path))[0] + "_norm.jpg"
            )
            img_final.save(out_path, "JPEG", quality=95)
            return out_path
    except Exception as e:
        raise ConvertError(f"تعذّر معالجة الصورة '{os.path.basename(path)}': {e}") from e


def images_to_pdf(
    image_paths: list[str],
    output_path: str,
    tmp_dir: str,
    progress_callback=None,
) -> str:
    """
    يحول قائمة صور مرتبة إلى ملف PDF واحد، كل صورة في صفحة مستقلة بنفس الترتيب.

    المعاملات:
        image_paths: قائمة مرتبة بمسارات الصور
        output_path: مسار حفظ ملف PDF الناتج
        tmp_dir: مجلد مؤقت لحفظ نسخ الصور المُعالجة (يُنشأ إذا لم يكن موجوداً)
        progress_callback: دالة اختيارية تُستدعى بـ (index, total, filename)
    """
    if not image_paths:
        raise ConvertError("لم يتم اختيار أي صور")

    for path in image_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"الملف غير موجود: {path}")
        if not is_supported_image(path):
            raise ConvertError(f"صيغة غير مدعومة: {os.path.basename(path)}")

    os.makedirs(tmp_dir, exist_ok=True)

    normalized_paths = []
    total = len(image_paths)
    for i, path in enumerate(image_paths, start=1):
        normalized_paths.append(_normalize_image(path, tmp_dir))
        if progress_callback:
            progress_callback(i, total, os.path.basename(path))

    try:
        pdf_bytes = img2pdf.convert(normalized_paths)
    except Exception as e:
        raise ConvertError(f"فشل إنشاء ملف PDF: {e}") from e

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    return output_path
