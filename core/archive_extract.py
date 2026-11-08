"""محرك فك ضغط الأرشيفات — يدعم صيغ عديدة بأمان (Archive Extract Engine)

الصيغ المدعومة:
  - النظام: zip, tar, tar.gz/tgz, tar.bz2/tbz2, tar.xz/txz, gz/bz2/xz المفردة
  - إضافية (إن توفرت المكتبة): 7z عبر py7zr، RAR عبر rarfile، zst عبر zstandard
حمايات: ثغرة Zip-Slip (تسريب مسارات) وأسماء ملفات عربية مشوهة في zip
"""

import os
import gzip
import bz2
import lzma
import shutil
import tarfile
import zipfile

try:
    import py7zr
    PY7ZR_AVAILABLE = True
except ImportError:
    py7zr = None
    PY7ZR_AVAILABLE = False

try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    rarfile = None
    RARFILE_AVAILABLE = False

try:
    import zstandard
    ZSTD_AVAILABLE = True
except ImportError:
    zstandard = None
    ZSTD_AVAILABLE = False


class ArchiveError(Exception):
    pass


# الامتدادات المقبولة (منها كتب المصورات cbz الشائعة لدى القارئ)
_ZIPLIKE = {'.zip', '.cbz'}
_TAR = {'.tar'}
_TARGZ = {'.tgz', '.tar.gz', '.taz'}
_TARBZ2 = {'.tbz2', '.tbz', '.tar.bz2'}
_TARXZ = {'.txz', '.tar.xz'}
_GZ = {'.gz'}
_BZ2 = {'.bz2'}
_XZ = {'.xz'}
_ZST = {'.zst'}
_7Z = {'.7z'}
_RAR = {'.rar', '.cbr'}

SUPPORTED_EXTS = sorted({
    *_ZIPLIKE, *_TAR, *_TARGZ, *_TARBZ2, *_TARXZ,
    *_GZ, *_BZ2, *_XZ, *_ZST, *_7Z, *_RAR,
})


def is_supported_archive(path: str) -> bool:
    """يتحقق هل الملف أرشيف مدعوم وفق الامتداد"""
    name = os.path.basename(path).lower()
    return any(name.endswith(ext) for ext in SUPPORTED_EXTS)


def archives_availability() -> dict:
    """تقرير جاهزية المكتبات الاختيارية — للعرض في الواجهة"""
    return {'7z': PY7ZR_AVAILABLE, 'rar': RARFILE_AVAILABLE, 'zstd': ZSTD_AVAILABLE}


def _unique_dir(dest: str) -> str:
    """يعيد مسار مجلد غير موجود (يضيف (1), (2)… عند التصادم)"""
    if not os.path.exists(dest):
        return dest
    n = 1
    while True:
        candidate = f"{dest} ({n})"
        if not os.path.exists(candidate):
            return candidate
        n += 1


def _safe_join(dest: str, entry_name: str) -> str | None:
    """يمنع ثغرة Zip-Slip: رفض المسارات الخارجة عن مجلد الهدف"""
    entry_name = entry_name.replace('\\', '/')
    if entry_name.startswith(('/', '~')) or ':' in entry_name.split('/')[0]:
        return None
    parts = [p for p in entry_name.split('/') if p not in ('', '.')]
    if any(p == '..' for p in parts):
        return None
    if not parts:  # مجلد جذر الأرشيف نفسه
        return None
    return os.path.join(dest, *parts)


def _fix_zip_name(info: zipfile.ZipInfo) -> str:
    """يصحح أسماء ملفات غير UTF-8 (العربية غالباً تظهر مشوهة)"""
    if info.flag_bits & 0x800 or not info.filename:
        return info.filename
    try:
        raw = info.filename.encode('cp437')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return info.filename
    for enc in ('utf-8', 'cp1256', 'cp1252'):
        try:
            decoded = raw.decode(enc)
            _ = decoded.encode(enc)  # تأكد أن الترميز المفسر يعود للأصل
            return decoded
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    return info.filename


def _is_within(base: str, target: str) -> bool:
    base_abs = os.path.abspath(base)
    target_abs = os.path.abspath(target)
    try:
        return os.path.commonpath([base_abs, target_abs]) == base_abs
    except ValueError:
        return False


# معالجات الإجمالي (العدد + الحجم الحالي) لكل صيغة
def _extract_zip(src: str, dest: str, progress=None) -> tuple[int, int]:
    files, skipped = 0, 0
    infos = []
    with zipfile.ZipFile(src) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            infos.append(info)
        total_bytes = sum(i.file_size for i in infos) or 1
        done_bytes = 0
        for info in infos:
            name = _fix_zip_name(info)
            target = _safe_join(dest, name)
            if target is None or not _is_within(dest, target):
                skipped += 1
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(info) as source, open(target, 'wb') as out:
                shutil.copyfileobj(source, out)
            files += 1
            done_bytes += info.file_size
            if progress:
                progress(f"📦 فك ضغط: {os.path.basename(name)}", int(done_bytes / total_bytes * 100))
    return files, skipped


def _extract_tar(src: str, mode: str, dest: str, progress=None) -> tuple[int, int]:
    files, skipped = 0, 0
    with tarfile.open(src, mode) as tf:
        members = [m for m in tf.getmembers() if m.isreg()]
        total = len(members) or 1
        for i, member in enumerate(members):
            target = _safe_join(dest, member.name)
            if target is None or not _is_within(dest, target):
                continue
            member.name = os.path.relpath(target, dest).replace('\\', '/')
            tf.extract(member, dest)
            files += 1
            if progress:
                progress(f"📦 فك ضغط: {os.path.basename(member.name)}", int((i + 1) / total * 100))
    return files, skipped


def _extract_7z(src: str, dest: str, progress=None) -> tuple[int, int]:
    if not PY7ZR_AVAILABLE:
        raise ArchiveError(
            "صيغة 7z تحتاج مكتبة py7zr.\nثبّتها بـ: pip install py7zr"
        )
    with py7zr.SevenZipFile(src, mode='r') as z:
        z.extractall(dest)
    files = sum(len(fnames) for _root, _dirs, fnames in os.walk(dest))
    return files, 0


def _extract_rar(src: str, dest: str, progress=None) -> tuple[int, int]:
    if not RARFILE_AVAILABLE:
        raise ArchiveError(
            "صيغة RAR تحتاج مكتبة rarfile وأداة فك الرار منافية.\nثبّتها بـ: pip install rarfile"
        )
    files = 0
    with rarfile.RarFile(src) as rf:
        members = [m for m in rf.infolist() if not m.is_dir()]
        total = len(members) or 1
        for i, m in enumerate(members):
            target = _safe_join(dest, m.filename)
            if target is None or not _is_within(dest, target):
                continue
            rf.extract(m, dest)
            files += 1
            if progress:
                progress(f"📦 فك ضغط: {os.path.basename(m.filename)}", int((i + 1) / total * 100))
    return files, 0


def _extract_zstd(src: str, dest: str, progress=None) -> tuple[int, int]:
    if not ZSTD_AVAILABLE:
        raise ArchiveError("صيغة zst تحتاج مكتبة zstandard.\nثبّتها بـ: pip install zstandard")
    out_path = os.path.join(dest, os.path.splitext(os.path.basename(src))[0])
    with open(src, 'rb') as fin, open(out_path, 'wb') as fout:
        dctx = zstandard.ZstdDecompressor()
        dctx.copy_stream(fin, fout)
    return 1, 0


def _extract_single_file(compressor, src: str, dest: str) -> tuple[int, int]:
    """يستخرج ملف شديد الضغط المفرد (example.txt.gz إلخ) باسمه الأصلي"""
    basename = os.path.basename(src)
    stem = basename
    for ext in ('.gz', '.bz2', '.xz'):
        if stem.endswith(ext):
            stem = stem[: -len(ext)]
            break
    out_path = os.path.join(dest, stem)
    with compressor.open(src, 'rb') as fin, open(out_path, 'wb') as fout:
        shutil.copyfileobj(fin, fout)
    return 1, 0


def extract_archive(src: str, dest_dir: str = None, progress=None) -> dict:
    """يفك ضغط أرشيف واحد

    dest_dir: مجلد الهدف الاختياري — الافتراضي: مجلد جديد باسم الأرشيف بجواره
    progress: دالة (message, percent) تستدعى أثناء العمل
    يعيد: {archive, dest, files, skipped}
    يرمي ArchiveError عند فشل صيغة أو تلف الأرشيف
    """
    if not os.path.isfile(src):
        raise ArchiveError(f"الملف غير موجود: {src}")
    name = os.path.basename(src).lower()
    if not is_supported_archive(src):
        raise ArchiveError(f"صيغة غير مدعومة: {os.path.basename(src)}")

    # اسم المجلد: اسم الأرشيف بدون الامتداد (الأطول أول المطابقة)
    base = os.path.basename(src)
    for ext in sorted(SUPPORTED_EXTS, key=len, reverse=True):
        if name.endswith(ext) and ext != name:
            base = base[: -len(ext)]
            break
    parent_dir = dest_dir if dest_dir else os.path.dirname(src)
    dest = _unique_dir(os.path.join(parent_dir, base))
    os.makedirs(dest, exist_ok=True)

    # اختيار المعالج حسب الصيغة (الأطول أولاً: tar.gz قبل gz)
    if any(name.endswith(e) for e in _ZIPLIKE):
        files, skipped = _extract_zip(src, dest, progress)
    elif any(name.endswith(e) for e in _TARGZ | _TARBZ2 | _TARXZ) or name.endswith('.tar'):
        mode = ('r:gz' if any(name.endswith(e) for e in _TARGZ)
                else 'r:bz2' if any(name.endswith(e) for e in _TARBZ2)
                else 'r:xz' if any(name.endswith(e) for e in _TARXZ)
                else 'r:')
        files, skipped = _extract_tar(src, mode, dest, progress)
    elif any(name.endswith(e) for e in _7Z):
        files, skipped = _extract_7z(src, dest, progress)
    elif any(name.endswith(e) for e in _RAR):
        files, skipped = _extract_rar(src, dest, progress)
    elif name.endswith('.zst'):
        files, skipped = _extract_zstd(src, dest, progress)
    elif name.endswith('.gz'):
        files, skipped = _extract_single_file(gzip, src, dest)
    elif name.endswith('.bz2'):
        files, skipped = _extract_single_file(bz2, src, dest)
    elif name.endswith('.xz'):
        files, skipped = _extract_single_file(lzma, src, dest)
    else:
        raise ArchiveError(f"صيغة غير مدعومة: {os.path.basename(src)}")

    return {'archive': src, 'dest': dest, 'files': files, 'skipped': skipped}


def extract_many(paths: list[str], dest_dir: str = None, progress=None) -> list[dict]:
    """يفك ضغط قائمة أرشيفات بالتتابع

    progress: دالة (message, percent) — نسبة مئوية عبر كل الأرشيفات
    يعيد قائمة نتائج لكل أرشف
    """
    results = []
    n = len(paths) or 1
    for i, p in enumerate(paths):
        try:
            result = extract_archive(
                p,
                dest_dir=dest_dir,
                progress=lambda msg, pct=None: progress(
                    f"({i + 1}/{n}) {msg}", int((i + (pct or 0) / 100) / n * 100)
                ) if progress else None,
            )
            results.append(result)
        except ArchiveError as e:
            results.append({'archive': p, 'dest': None, 'files': 0,
                            'skipped': 0, 'error': str(e)})
    return results
