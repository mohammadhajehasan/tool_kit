"""سجل أخطاء محلي + معالج استثناءات عام مع نوافذ ودّية."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def _log_dir() -> str:
    """logs/ مستقر: بجانب المصدر، أو في %LOCALAPPDATA% داخل exe المجمّع.

    في PyInstaller onefile يكون مجلد الملف المؤقت — يُحذف عند الإغلاق — لذلك
    نحتاج مجلداً دائماً للسجل حتى تبقى تفاصيل الأعطال قابلة للفحص.
    """
    if getattr(sys, "frozen", False):
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PDF_Toolbox", "logs")
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "logs")


LOG_DIR = _log_dir()
LOG_PATH = os.path.join(LOG_DIR, "app.log")


def setup():
    """يضبط تسجيل الدخول إلى ملف متناوب في مجلد logs/."""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        return
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return
    handler = RotatingFileHandler(LOG_PATH, maxBytes=512 * 1024, backupCount=2, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root.addHandler(handler)


def log_exception(prefix: str = "استثناء غير معالج"):
    logging.getLogger("pdf_toolbox").error(prefix, exc_info=sys.exc_info())


def install_excepthook():
    """
    يلتقط أي خطأ غير معالج في الواجهة، يسجّله، ويعرض نافذة ودّية
    فيها: فتح ملف السجل / إبلاغ المطور.
    """
    def hook(etype, value, tb):
        try:
            logging.getLogger("pdf_toolbox").critical("خطأ غير معالج", exc_info=(etype, value, tb))
        except Exception:
            pass
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            from version import APP_VERSION
            from ui.i18n import tr_text, tr_fmt

            if QApplication.instance() is None:
                return
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(tr_text("PDF Toolbox — خطأ غير متوقع"))
            msg.setText(tr_text("حدث خطأ غير متوقع وتم تسجيل التفاصيل في ملف السجل."))
            msg.setInformativeText(tr_text("يمكنك إبلاغ المطور مع تفاصيل الخطأ."))
            open_log = msg.addButton(tr_text("📂 فتح ملف السجل"), QMessageBox.ActionRole)
            report = msg.addButton(tr_text("✉️ إبلاغ المطور"), QMessageBox.ActionRole)
            msg.addButton(tr_text("إغلاق"), QMessageBox.RejectRole)
            msg.exec()
            clicked = msg.clickedButton()
            if clicked is open_log and os.path.isfile(LOG_PATH):
                os.startfile(LOG_PATH)
            elif clicked is report:
                subject = tr_fmt("PDF Toolbox v{version} — مشكلة", version=APP_VERSION)
                body = tr_text("السلام عليكم، واجهتني هذه المشكلة في التطبيق:\n\n(اشرح ما كنت تفعله)\n\n")
                try:
                    with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
                        tail = f.read()[-1500:]
                    body += tr_text("--- آخر السجل ---\n") + tail
                except Exception:
                    pass
                from urllib.parse import quote
                QDesktopServices.openUrl(QUrl(
                    "mailto:ahmadalfarahat099175@gmail.com?subject="
                    + quote(subject) + "&body=" + quote(body)))
        except Exception:
            pass

    sys.excepthook = hook
