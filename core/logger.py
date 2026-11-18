"""سجل أخطاء محلي + معالج استثناءات عام مع نوافذ ودّية."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(_BASE, "logs")
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

            if QApplication.instance() is None:
                return
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("PDF Toolbox — خطأ غير متوقع")
            msg.setText("حدث خطأ غير متوقع وتم تسجيل التفاصيل في ملف السجل.")
            msg.setInformativeText("يمكنك إبلاغ المطور مع تفاصيل الخطأ.")
            open_log = msg.addButton("📂 فتح ملف السجل", QMessageBox.ActionRole)
            report = msg.addButton("✉️ إبلاغ المطور", QMessageBox.ActionRole)
            msg.addButton("إغلاق", QMessageBox.RejectRole)
            msg.exec()
            clicked = msg.clickedButton()
            if clicked is open_log and os.path.isfile(LOG_PATH):
                os.startfile(LOG_PATH)
            elif clicked is report:
                subject = f"PDF Toolbox v{APP_VERSION} — مشكلة"
                body = "السلام عليكم، واجهتني هذه المشكلة في التطبيق:\n\n(اشرح ما كنت تفعله)\n\n"
                try:
                    with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
                        tail = f.read()[-1500:]
                    body += "--- آخر السجل ---\n" + tail
                except Exception:
                    pass
                from urllib.parse import quote
                QDesktopServices.openUrl(QUrl(
                    "mailto:ahmadalfarahat099175@gmail.com?subject="
                    + quote(subject) + "&body=" + quote(body)))
        except Exception:
            pass

    sys.excepthook = hook
