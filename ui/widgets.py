"""مكونات واجهة مشتركة — تصميم عصري"""

import os
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QWidget, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QThread, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent


class DropZone(QFrame):
    """منطقة سحب وإفلات للملفات — تصميم عصري"""

    filesDropped = Signal(list)

    def __init__(self, hint_text="اسحب الملفات هنا أو انقر للاختيار",
                  sub_text="", file_filter="All Files (*)", multiple=True,
                  min_height=170, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setFixedHeight(min_height)
        self.file_filter = file_filter
        self.multiple = multiple
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        icon = QLabel("📂")
        icon.setObjectName("dropIcon")
        icon.setAlignment(Qt.AlignCenter)

        text = QLabel(hint_text)
        text.setObjectName("dropText")
        text.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(text)

        if sub_text:
            sub = QLabel(sub_text)
            sub.setObjectName("dropSubtext")
            sub.setAlignment(Qt.AlignCenter)
            layout.addWidget(sub)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.filesDropped.emit(paths)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._open_dialog()
        super().mousePressEvent(event)

    def _open_dialog(self):
        if self.multiple:
            paths, _ = QFileDialog.getOpenFileNames(self, "اختر الملفات", "", self.file_filter)
        else:
            path, _ = QFileDialog.getOpenFileName(self, "اختر ملف", "", self.file_filter)
            paths = [path] if path else []
        if paths:
            self.filesDropped.emit(paths)


class FileListWidget(QListWidget):
    """قائمة ملفات مع إمكانية إعادة الترتيب بالسحب وحذف عناصر"""

    filesChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fileList")
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setIconSize(QSize(28, 28))
        self.file_paths: list[str] = []
        self.model().rowsMoved.connect(self._sync_order)

    def add_files(self, paths: list[str]):
        for p in paths:
            if p and p not in self.file_paths and os.path.isfile(p):
                self.file_paths.append(p)
                item = QListWidgetItem(f"  {os.path.basename(p)}")
                item.setData(Qt.UserRole, p)
                item.setToolTip(p)
                self.addItem(item)
        self.filesChanged.emit()

    def remove_selected(self):
        for item in self.selectedItems():
            path = item.data(Qt.UserRole)
            if path in self.file_paths:
                self.file_paths.remove(path)
            self.takeItem(self.row(item))
        self.filesChanged.emit()

    def clear_all(self):
        self.clear()
        self.file_paths = []
        self.filesChanged.emit()

    def _sync_order(self, *args):
        """يعيد بناء قائمة المسارات حسب الترتيب الجديد بعد السحب اليدوي"""
        new_order = []
        for i in range(self.count()):
            path = self.item(i).data(Qt.UserRole)
            new_order.append(path)
        self.file_paths = new_order
        self.filesChanged.emit()

    def get_paths(self) -> list[str]:
        return list(self.file_paths)


class Worker(QThread):
    """خيط تنفيذ منفصل لتشغيل عمليات معالجة الملفات بدون تجميد الواجهة"""

    finished_ok = Signal(object)
    failed = Signal(str)
    progress = Signal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.finished_ok.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


def make_toolbar_button(text: str, danger=False) -> QPushButton:
    btn = QPushButton(text)
    if danger:
        btn.setObjectName("dangerBtn")
    return btn
