"""
أداة PDF - تطبيق سطح مكتب لضغط، تقطيع، دمج، وتحويل ملفات PDF
نقطة الدخول الرئيسية للتطبيق
"""

import sys
import os
import json

# يضمن استيراد الحزم الداخلية (core, ui) بشكل صحيح سواء عند التشغيل
# المباشر بـ Python أو بعد التجميع كـ exe عبر PyInstaller
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# تحميل الإعدادات المحفوظة
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
try:
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        SETTINGS = json.load(f)
except Exception:
    SETTINGS = {"theme": "auto"}

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from ui.styles import get_style


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Toolbox")

    # تعيين الثيم باستخدام النظام الحديث
    try:
        theme = SETTINGS.get("theme", "auto")
    except NameError:
        theme = "auto"
    app.setStyleSheet(get_style(theme))

    # رمز التطبيق
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icons", "app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
