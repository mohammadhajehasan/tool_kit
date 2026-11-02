"""
أداة PDF - تطبيق سطح مكتب لضغط، تقطيع، دمج، وتحويل ملفات PDF
نقطة الدخول الرئيسية للتطبيق
"""

import sys
import os

# يضمن استيراد الحزم الداخلية (core, ui) بشكل صحيح سواء عند التشغيل
# المباشر بـ Python أو بعد التجميع كـ exe عبر PyInstaller
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("أداة PDF")

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icons", "app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
