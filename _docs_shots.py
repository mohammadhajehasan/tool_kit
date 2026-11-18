# توليد لقطات نهائية موثّقة التسمية: لاحقة _light/_dark تطابق الثيم فعلياً
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

app = QApplication(sys.argv)
app.setLayoutDirection(Qt.RightToLeft)

from ui.main_window import MainWindow

win = MainWindow()
win.show()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "screenshots")
os.makedirs(out, exist_ok=True)

ROWS = {}
for i in range(win.sidebar.count()):
    k = win.sidebar.item(i).data(Qt.UserRole)
    if k:
        ROWS[k] = i

SHOTS = [
    # (اسم الملف, أداة, ثيم)
    ("01_compress_light", "compress", "light"),
    ("02_compress_dark", "compress", "dark"),
    ("03_split_dark", "split", "dark"),
    ("04_merge_light", "merge", "light"),
    ("05_convert_dark", "convert", "dark"),
    ("06_pdf2img_light", "pdf2img", "light"),
    ("07_extract_dark", "extract", "dark"),
    ("08_ocr_light", "ocr", "light"),
    ("09_pages_dark", "pages", "dark"),
    ("10_stamp_light", "stamp", "light"),
    ("11_protect_dark", "protect", "dark"),
    ("12_repair_light", "repair", "light"),
    ("13_archive_dark", "archive", "dark"),
    ("14_info_light", "info", "light"),
    ("15_export_dark", "export", "dark"),
    ("16_diff_light", "diff", "light"),
    ("17_ai_dark", "ai", "dark"),
]

idx = 0

def step():
    global idx
    if idx >= len(SHOTS):
        print("DONE")
        app.quit()
        return
    name, tool, theme = SHOTS[idx]
    win.theme_setting = theme
    win._apply_style()
    win.sidebar.setCurrentRow(ROWS[tool])
    def grab():
        global idx
        pix = win.grab()
        path = os.path.join(out, name + ".png")
        pix.save(path)
        print("saved", path)
        idx += 1
        QTimer.singleShot(30, step)
    QTimer.singleShot(60, grab)

QTimer.singleShot(500, step)
app.exec()
