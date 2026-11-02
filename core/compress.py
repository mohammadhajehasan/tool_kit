"""
وحدة ضغط ملفات PDF
تستخدم PyMuPDF (الأساسية) لضغط فعّال، مع خيار Ghostscript للضغط الأقوى.

الاستراتيجية (PyMuPDF المدمجة):
1. يعيد ترميز الصور المدمجة إلى JPEG بجودة مناسبة
2. يحافظ على النصوص كنصوص (لا يحوّلها لصور)
3. يقلّل دقة الصور الكبيرة فقط (حسب المستوى)
4. يحفظ مع تنظيف (garbage collection) وضغط Flate

ملاحظة: الحفاظ على قابلية القراءة والجودة هو الأولوية القصوى.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class CompressError(Exception):
    """يُرفع عند فشل عملية الضغط"""
    pass


# إعدادات الصور لكل مستوى ضغط
IMAGE_SETTINGS = {
    # quality: جودة JPEG لإعادة ترميز الصور (أعلى = جودة أفضل، حجم أكبر)
    # dpi_threshold: الحدّ الذي تبدأ عنده تقليل دقة الصور
    # dpi_target: الدقة المستهدفة للصور الكبيرة (أقل = أصغر حجم)
    "recommended": {"quality": 75, "dpi_target": 120, "dpi_threshold": 150},
    "extreme":     {"quality": 55, "dpi_target": 72, "dpi_threshold": 100},
}


def find_ghostscript() -> str:
    """
    يبحث عن مسار Ghostscript القابل للتنفيذ.
    يدعم ويندوز (gswin64c / gswin32c) ولينكس/ماك (gs).
    """
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    bundled_candidates = [
        base_dir / "resources" / "gs" / "gswin64c.exe",
        base_dir / "resources" / "gs" / "gswin32c.exe",
        base_dir / "resources" / "gs" / "gs",
    ]
    for candidate in bundled_candidates:
        if candidate.exists():
            return str(candidate)

    names = ["gswin64c", "gswin32c", "gs"] if os.name == "nt" else ["gs"]
    for name in names:
        path = shutil.which(name)
        if path:
            return path

    return None


def get_file_size(path: str) -> int:
    """يرجع حجم الملف بالبايت"""
    return os.path.getsize(path)


def ghostscript_available() -> bool:
    """يرجع True إذا كان Ghostscript متاحاً على النظام"""
    return find_ghostscript() is not None


def _compress_with_pymupdf(input_path: str, output_path: str, level: str,
                           progress_callback=None) -> dict:
    """
    الضغط الفعّال باستخدام PyMuPDF.
    يعيد ترميز الصور المدمجة إلى JPEG بجودة مناسبة، مع الحفاظ على النصوص
    كنصوص، وتقليل دقة الصور الكبيرة فقط.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise CompressError(
            "PyMuPDF غير مثبّت. ثبّته: pip install pymupdf"
        )

    if progress_callback:
        progress_callback()

    settings = IMAGE_SETTINGS[level]
    quality = settings["quality"]
    dpi_target = settings.get("dpi_target")
    dpi_threshold = settings.get("dpi_threshold")

    original_size = get_file_size(input_path)

    try:
        doc = fitz.open(input_path)

        kwargs = dict(
            lossy=True,
            lossless=True,
            bitonal=True,
            color=True,
            gray=True,
            quality=quality,
        )
        # تقليل دقة الصور الكبيرة فقط
        if dpi_target and dpi_threshold:
            kwargs["dpi_threshold"] = dpi_threshold
            kwargs["dpi_target"] = dpi_target

        doc.rewrite_images(**kwargs)

        # الحفظ مع تنظيف وضغط
        doc.save(
            output_path,
            garbage=4,          # تنظيف كامل للمحتوى غير المستخدم
            deflate=True,       # ضغط Flate للـ streams
            clean=True,         # تنظيف البنية
            pretty=False,
        )
        doc.close()

    except Exception as e:
        raise CompressError(f"فشل الضغط عبر PyMuPDF: {e}") from e

    if not os.path.isfile(output_path):
        raise CompressError("لم يتم إنشاء الملف الناتج")

    compressed_size = get_file_size(output_path)
    reduction_percent = 0.0
    if original_size > 0:
        reduction_percent = round((1 - (compressed_size / original_size)) * 100, 1)

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "reduction_percent": reduction_percent,
    }


def _compress_with_ghostscript(input_path: str, output_path: str, level: str,
                               progress_callback=None) -> dict:
    """الضغط باستخدام Ghostscript"""
    gs_exe = find_ghostscript()
    if not gs_exe:
        raise CompressError("Ghostscript not found")

    gs_setting = "/ebook" if level == "recommended" else "/screen"
    cmd = [
        gs_exe,
        "-sDEVICE=pdfwrite",
        f"-dPDFSETTINGS={gs_setting}",
        "-dCompatibilityLevel=1.4",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        "-dSAFER",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        "-dCompressPages=true",
        "-dDetectDuplicateImages=true",
        "-dAutoFilterColorImages=false",
        "-dColorImageFilter=/DCTEncode",
        "-dAutoFilterGrayImages=false",
        "-dGrayImageFilter=/DCTEncode",
        "-dMonoImageFilter=/CCITTFaxEncode",
        "-dDownsampleColorImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleMonoImages=true",
    ]

    if level == "extreme":
        cmd += [
            "-dColorImageResolution=100",
            "-dGrayImageResolution=100",
            "-dMonoImageResolution=300",
        ]
    else:
        cmd += [
            "-dColorImageResolution=150",
            "-dGrayImageResolution=150",
            "-dMonoImageResolution=300",
        ]

    cmd += [f"-sOutputFile={output_path}", input_path]

    if progress_callback:
        progress_callback()

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
    except subprocess.CalledProcessError as e:
        raise CompressError(f"فشل الضغط عبر Ghostscript: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise CompressError("انتهت مهلة عملية الضغط (الملف كبير جداً)") from e

    if not os.path.isfile(output_path):
        raise CompressError("لم يتم إنشاء الملف الناتج")

    original_size = get_file_size(input_path)
    compressed_size = get_file_size(output_path)
    reduction_percent = 0.0
    if original_size > 0:
        reduction_percent = round((1 - (compressed_size / original_size)) * 100, 1)

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "reduction_percent": reduction_percent,
    }


def _compress_with_pikepdf(input_path: str, output_path: str, level: str,
                            progress_callback=None) -> dict:
    """بديل آمن: ضغط streams وFlate فقط (لا يلمس الصور)"""
    try:
        import pikepdf
        from pikepdf import Pdf, PdfError
    except ImportError:
        raise CompressError(
            "لا توجد أي أداة ضغط متاحة. ثبّت pymupdf أو pikepdf."
        )

    if progress_callback:
        progress_callback()

    original_size = get_file_size(input_path)

    try:
        pdf = Pdf.open(input_path)
        pdf.save(
            output_path,
            compress_streams=True,
            recompress_flate=True,
        )
        pdf.close()
    except PdfError as e:
        raise CompressError(f"فشل قراءة ملف PDF: {e}") from e
    except Exception as e:
        raise CompressError(f"فشل الضغط عبر pikepdf: {e}") from e

    if not os.path.isfile(output_path):
        raise CompressError("لم يتم إنشاء الملف الناتج")

    compressed_size = get_file_size(output_path)
    reduction_percent = 0.0
    if original_size > 0:
        reduction_percent = round((1 - (compressed_size / original_size)) * 100, 1)

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "reduction_percent": reduction_percent,
    }


def compress_pdf(
    input_path: str,
    output_path: str,
    level: str = "recommended",
    use_ghostscript: bool = False,
    progress_callback=None,
) -> dict:
    """
    يضغط ملف PDF ويحفظ النتيجة في output_path.
    الافتراضي: PyMuPDF (ضغط فعّال للصور).
    إذا طُلب use_ghostscript وكان متاحاً، يستخدم Ghostscript للضغط الأقوى.
    أخيراً: pikepdf كبديل احتياطي آمن.

    يرجع dict يحتوي:
        original_size, compressed_size, reduction_percent, method
    """
    if level not in IMAGE_SETTINGS:
        raise ValueError(f"مستوى ضغط غير معروف: {level}")

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")

    # 1) Ghostscript إذا طُلب صراحةً وكان متاحاً
    if use_ghostscript:
        gs_exe = find_ghostscript()
        if gs_exe:
            try:
                result = _compress_with_ghostscript(input_path, output_path, level, progress_callback)
                result["method"] = "Ghostscript"
                return result
            except CompressError:
                pass  # ننتقل إلى البديل

    # 2) PyMuPDF — الضغط الافتراضي الفعّال
    try:
        result = _compress_with_pymupdf(input_path, output_path, level, progress_callback)
        result["method"] = "PyMuPDF"
        return result
    except CompressError:
        pass

    # 3) pikepdf — بديل احتياطي
    result = _compress_with_pikepdf(input_path, output_path, level, progress_callback)
    result["method"] = "pikepdf"
    return result


def format_size(num_bytes: int) -> str:
    """يحول حجم البايتات إلى صيغة مقروءة (KB, MB...)"""
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
