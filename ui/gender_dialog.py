"""
حوار اختيار الجنس (الذكر / الأنثى)
يستخدم لتخصيص لون التطبيق وخط الصور حسب تفضيل المستخدم.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt


class GenderDialog(QDialog):
    """
    حوار يطلب من المستخدم اختيار جنسه (ذكر/أنثى) لتخصيص مظهر التطبيق.
    يرجع عبر get_gender() قيمة "male" أو "female".
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("اختر الجنس")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(460, 380)
        self.selected_gender = "male"

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 28, 28, 28)

        title = QLabel("👋  مرحباً بك!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a;")
        layout.addWidget(title)

        subtitle = QLabel(
            "اختر الجنس لتخصيص ألوان التطبيق وتجربتك المميزة"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; font-size: 13px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # بطاقتا الاختيار
        self.group = QButtonGroup(self)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.male_card = self._make_card("👨", "ذكر", "male")
        self.female_card = self._make_card("👩", "أنثى", "female")
        self.group.addButton(self.male_card.radio)
        self.group.addButton(self.female_card.radio)

        cards_layout.addWidget(self.male_card)
        cards_layout.addWidget(self.female_card)
        layout.addLayout(cards_layout)

        layout.addStretch()

        # زر التأكيد
        confirm_btn = QPushButton("متابعة")
        confirm_btn.setObjectName("primaryBtn")
        confirm_btn.clicked.connect(self._on_confirm)
        layout.addWidget(confirm_btn)

    def _make_card(self, emoji, label, value):
        card = QFrame()
        card.setObjectName("optionCard")
        card.setProperty("selected", value == "male")
        card.setCursor(Qt.PointingHandCursor)

        v = QVBoxLayout(card)
        v.setAlignment(Qt.AlignCenter)
        v.setSpacing(8)
        v.setContentsMargins(16, 20, 16, 20)

        emoji_lbl = QLabel(emoji)
        emoji_lbl.setAlignment(Qt.AlignCenter)
        emoji_lbl.setStyleSheet("font-size: 40px;")

        radio = QRadioButton(label)
        radio.setChecked(value == "male")
        radio.setStyleSheet("font-size: 15px; font-weight: 700;")

        v.addWidget(emoji_lbl)
        v.addWidget(radio)

        card.radio = radio
        card.value = value
        radio.toggled.connect(lambda checked, c=card, w=value: self._on_card_toggled(c, checked, w))

        return card

    def _on_card_toggled(self, card, checked, value):
        if checked:
            self.selected_gender = value
            # تحديث تمييز البطاقات
            self.male_card.setProperty("selected", self.male_card.radio.isChecked())
            self.female_card.setProperty("selected", self.female_card.radio.isChecked())
            self.male_card.style().unpolish(self.male_card)
            self.female_card.style().unpolish(self.female_card)
            self.male_card.style().polish(self.male_card)
            self.female_card.style().polish(self.female_card)

    def get_gender(self) -> str:
        """يرجع الجنس المختار: 'male' أو 'female'"""
        return self.selected_gender

    def _on_confirm(self):
        self.accept()


def ask_gender(parent=None) -> str:
    """
    يعرض حوار اختيار الجنس ويُرجع "male" أو "female".
إذا أُغلق الحوار بدون اختيار، يُرجع "male" افتراضياً.
    """
    dlg = GenderDialog(parent)
    if dlg.exec() == QDialog.Accepted:
        return dlg.get_gender()
    return "male"
