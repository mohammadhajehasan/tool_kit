"""لوحة الانتقال السريع (Ctrl+K) — بحث فوري في الأدوات."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel,
)
from PySide6.QtCore import Qt

from ui.i18n import tr


class CommandPalette(QDialog):
    """نافذة بحث سريعة للقفز إلى أي أداة."""

    def __init__(self, actions: list[tuple[str, str]], parent=None):
        """
        actions: [(label, key)] — يُستدعى main_window.jump_to(key) عند الاختيار.
        """
        super().__init__(parent)
        self.jump_callback = None
        self.setWindowTitle(tr("palette_title"))
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setMaximumHeight(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("palette_hint"))
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.setObjectName("paletteList")
        self.list.itemActivated.connect(self._pick)
        for label, key in actions:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            self.list.addItem(item)
        if self.list.count():
            self.list.setCurrentRow(0)
        layout.addWidget(self.list)

        hint = QLabel("Enter للانتقال  •  Esc للإغلاق")
        hint.setObjectName("hintLabel")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

    def _filter(self, text):
        text = text.strip().lower()
        for i in range(self.list.count()):
            item = self.list.item(i)
            label = item.text().lower()
            key = (item.data(Qt.UserRole) or "").lower()
            match = text in label or text in key
            item.setHidden(not match)
        visible_rows = [i for i in range(self.list.count()) if not self.list.item(i).isHidden()]
        if visible_rows:
            self.list.setCurrentRow(visible_rows[0])

    def _pick(self, item):
        key = item.data(Qt.UserRole)
        self.accept()
        if self.jump_callback:
            self.jump_callback(key)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            item = self.list.currentItem()
            if item:
                self._pick(item)
            return
        if event.key() == Qt.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)
