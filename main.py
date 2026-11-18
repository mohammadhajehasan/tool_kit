"""
أداة PDF — تطبيق سطح مكتب لمعالجة ملفات PDF
نقطة الدخول: تشغيل الواجهة أو تنفيذ أوامر من سطر الأوامر (CLI).
"""

import sys
import os
import json

# يضمن استيراد الحزم الداخلية (core, ui) بشكل صحيح سواء عند التشغيل
# المباشر بـ Python أو بعد التجميع كـ exe عبر PyInstaller
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup as setup_logging, install_excepthook

setup_logging()

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
try:
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        SETTINGS = json.load(f)
except Exception:
    SETTINGS = {"theme": "auto"}


# ================= سطر الأوامر (CLI) =================
def run_cli(argv: list[str]) -> int:
    """ينفذ عملية على ملفات مباشرة من سطر الأوامر ثم يخرج (بلا واجهة)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    import argparse
    p = argparse.ArgumentParser(prog="PDF_Toolbox", description="PDF Toolbox CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compress", help="ضغط ملف PDF")
    c.add_argument("input")
    c.add_argument("-o", "--out", default=None)
    c.add_argument("--level", choices=["light", "recommended", "extreme"], default="recommended")
    c.add_argument("--gs", action="store_true", help="استخدم Ghostscript إن توفر")

    m = sub.add_parser("merge", help="دمج عدة ملفات")
    m.add_argument("inputs", nargs="+")
    m.add_argument("-o", "--out", required=True)

    s = sub.add_parser("split", help="تقطيع PDF")
    s.add_argument("input")
    s.add_argument("--pages", default=None, help='نطاقات مثل "1-3,5"')
    s.add_argument("--each", action="store_true", help="كل صفحة ملف مستقل")
    s.add_argument("--bookmarks", action="store_true", help="حسب الفصول (الفهرس)")
    s.add_argument("-d", "--outdir", default=None)

    cv = sub.add_parser("convert", help="صور إلى PDF")
    cv.add_argument("inputs", nargs="+")
    cv.add_argument("-o", "--out", required=True)

    p2i = sub.add_parser("pdf2img", help="PDF إلى صور")
    p2i.add_argument("input")
    p2i.add_argument("--fmt", choices=["jpg", "png"], default="jpg")
    p2i.add_argument("--dpi", type=int, default=150)
    p2i.add_argument("--quality", type=int, default=85)
    p2i.add_argument("-d", "--outdir", default=None)

    pr = sub.add_parser("protect", help="تشفير/فك تشفير PDF")
    pr.add_argument("input")
    pr.add_argument("-o", "--out", default=None)
    pr.add_argument("--password", required=True)
    pr.add_argument("--remove", action="store_true", help="إزالة الحماية بدل إضافتها")
    pr.add_argument("--allow-copy", action="store_true")

    st = sub.add_parser("stamp", help="علامة مائية وترقيم")
    st.add_argument("input")
    st.add_argument("-o", "--out", default=None)
    st.add_argument("--watermark", default=None, help="نص العلامة المائية")
    st.add_argument("--image", default=None, help="صورة العلامة المائية")
    st.add_argument("--angle", type=int, default=30)
    st.add_argument("--opacity", type=float, default=0.3)
    st.add_argument("--number", choices=["x", "dash", "page_of_en", "page_of_ar"],
                    default=None, help="صيغة الترقيم")

    ex = sub.add_parser("extract", help="استخراج نص/صور")
    ex.add_argument("input")
    ex.add_argument("--text", action="store_true")
    ex.add_argument("--images", action="store_true")
    ex.add_argument("-d", "--outdir", default=None)

    rp = sub.add_parser("repair", help="إصلاح ملف تالف")
    rp.add_argument("input")
    rp.add_argument("-o", "--out", default=None)

    args = p.parse_args(argv)

    from core import compress as C
    out_default = lambda inp, suffix: os.path.splitext(inp)[0] + suffix  # noqa: E731

    if args.cmd == "compress":
        out = args.out or out_default(args.input, "_مضغوط.pdf")
        r = C.compress_pdf(args.input, out, level=args.level, use_ghostscript=args.gs)
        print(f"OK method={r['method']} reduction={r['reduction_percent']}%")
        print(f"OUT {os.path.abspath(out)}")

    elif args.cmd == "merge":
        from core.merge import merge_pdfs
        r = merge_pdfs(args.inputs, args.out)
        print(f"OK pages={r.get('pages', '?')}" if isinstance(r, dict) else "OK")
        print(f"OUT {os.path.abspath(args.out)}")

    elif args.cmd == "split":
        from core import split as S
        outdir = args.outdir or (os.path.dirname(args.input) or ".")
        base = os.path.splitext(args.input)[0]
        if args.bookmarks:
            files = S.split_by_bookmarks(args.input, outdir)
        elif args.each:
            files = S.split_to_individual_files(args.input, outdir)
        elif args.pages:
            out = base + "_صفحات_مختارة.pdf"
            S.extract_pages(args.input, S.parse_page_ranges(args.pages, S.get_page_count(args.input)), out)
            files = [out]
        else:
            p.error("حدد --pages أو --each أو --bookmarks")
        print(f"OK files={len(files)}")
        for f in files:
            print(f"OUT {os.path.abspath(f)}")

    elif args.cmd == "convert":
        from core.convert import images_to_pdf
        images_to_pdf(args.inputs, args.out)
        print("OK")
        print(f"OUT {os.path.abspath(args.out)}")

    elif args.cmd == "pdf2img":
        from core.pdf2img import pdf_to_images
        outdir = args.outdir or os.path.splitext(args.input)[0] + "_صور"
        files = pdf_to_images(args.input, outdir, fmt=args.fmt, dpi=args.dpi, quality=args.quality)
        print(f"OK files={len(files)}")
        for f in files[:5]:
            print(f"OUT {os.path.abspath(f)}")

    elif args.cmd == "protect":
        from core.protect import protect, unprotect
        out = args.out or out_default(args.input, "_محمي.pdf" if not args.remove else "_بدون_حماية.pdf")
        if args.remove:
            unprotect(args.input, out, args.password)
        else:
            protect(args.input, out, user_password=args.password,
                    allow_print=True, allow_copy=args.allow_copy)
        print("OK")
        print(f"OUT {os.path.abspath(out)}")

    elif args.cmd == "stamp":
        from core.stamp import watermark, add_page_numbers
        src = args.input
        tmp = None
        if args.watermark or args.image:
            tmp = out_default(args.input, "_wm_tmp.pdf")
            watermark(src, tmp, text=args.watermark, image_path=args.image,
                      opacity=args.opacity, angle=args.angle)
            src = tmp
        out = args.out or out_default(args.input, "_نهائي.pdf")
        if args.number:
            add_page_numbers(src, out, mode=args.number)
        elif tmp:
            os.replace(tmp, out)
        else:
            p.error("حدد --watermark أو --image أو --number")
        if tmp and os.path.exists(tmp) and tmp != out:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        print("OK")
        print(f"OUT {os.path.abspath(out)}")

    elif args.cmd == "extract":
        from core.extract import extract_text, extract_images
        stem = os.path.splitext(args.input)[0]
        if args.text:
            r = extract_text(args.input, stem + ".txt")
            print(f"OK chars={r['chars']}")
            print(f"OUT {os.path.abspath(r['out'])}")
        elif args.images:
            outdir = args.outdir or stem + "_صور"
            r = extract_images(args.input, outdir)
            print(f"OK images={r['count']}")
            print(f"DIR {os.path.abspath(r['dir'])}")
        else:
            p.error("حدد --text أو --images")

    elif args.cmd == "repair":
        from core.repair import repair
        out = args.out or out_default(args.input, "_مصلح.pdf")
        r = repair(args.input, out)
        print(f"OK engine={r['engine']} size={r['size']}")
        print(f"OUT {os.path.abspath(r['out'])}")

    return 0


def restart_app():
    """يعيد تشغيل التطبيق (بعد تغيير اللغة مثلاً)."""
    import subprocess
    if getattr(sys, "frozen", False):
        subprocess.Popen([sys.executable])
    else:
        subprocess.Popen([sys.executable, os.path.abspath(__file__)])
    from PySide6.QtWidgets import QApplication
    QApplication.instance().quit()


def main():
    # CLI إذا وُجدت وسائط (ما عدا --gui القسري)
    if len(sys.argv) > 1:
        sys.exit(run_cli(sys.argv[1:]))

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from ui import i18n
    from ui.styles import get_style

    app = QApplication(sys.argv)
    app.setApplicationName("PDF Toolbox")

    # اتجاه الواجهة حسب اللغة
    app.setLayoutDirection(Qt.RightToLeft if i18n.rtl() else Qt.LeftToRight)

    app.setStyleSheet(get_style(SETTINGS.get("theme", "auto")))

    # رمز التطبيق
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icons", "app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    install_excepthook()

    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    # فحص تحديث هادئ بعد 3 ثوانٍ من الإقلاع
    try:
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, window._auto_update_check)
    except Exception:
        pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
