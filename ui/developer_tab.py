"""تبويب عن المطور — بطاقة تعريفية وبيانات تواصل قابلة للنقر"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices


class ContactRow(QFrame):
    """صف تواصل: أيقونة + وصف + قيمة قابلة للنقر"""

    def __init__(self, icon: str, label: str, value: str, url: str = None, parent=None):
        super().__init__(parent)
        self.setObjectName("contactRow")
        self.url = url

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 8, 16, 8)
        row.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("contactIcon")
        icon_lbl.setFixedWidth(34)
        icon_lbl.setAlignment(Qt.AlignCenter)
        row.addWidget(icon_lbl)

        name_lbl = QLabel(label)
        name_lbl.setObjectName("contactLabel")
        name_lbl.setFixedWidth(90)
        row.addWidget(name_lbl)

        value_lbl = QLabel(value)
        value_lbl.setObjectName("contactValue")
        value_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row.addWidget(value_lbl, 1)

        if url:
            open_btn = QPushButton("فتح")
            open_btn.setObjectName("secondaryBtn")
            open_btn.setCursor(Qt.PointingHandCursor)
            open_btn.setFixedHeight(34)
            open_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
            row.addWidget(open_btn)


class DeveloperTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("عن المطور")
        title.setObjectName("pageTitle")
        desc = QLabel("صاحب الفضل في تصميم وتطوير هذا النظام")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        # ===== بطاقة التعريف =====
        card = QFrame()
        card.setObjectName("aboutCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignHCenter)

        avatar = QLabel("🧑‍💻")
        avatar.setObjectName("avatarLabel")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(76, 76)

        name = QLabel("المهندس أحمد مصطفى الفرحات")
        name.setObjectName("heroName")
        name.setAlignment(Qt.AlignCenter)

        role = QLabel(
            "مهندس علوم حاسب — تطوير برمجيات وأنظمة تعمل بالذكاء الاصطناعي"
        )
        role.setObjectName("heroRole")
        role.setWordWrap(True)
        role.setAlignment(Qt.AlignCenter)

        credit = QLabel("مصمم ومطور نظام أداة PDF بالكامل")
        credit.setObjectName("hintLabel")
        credit.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(avatar, 0, Qt.AlignHCenter)
        card_layout.addWidget(name)
        card_layout.addWidget(role)
        card_layout.addWidget(credit)
        layout.addWidget(card)

        # ===== بطاقة التواصل =====
        contacts = QFrame()
        contacts.setObjectName("aboutCard")
        contacts_layout = QVBoxLayout(contacts)
        contacts_layout.setContentsMargins(12, 10, 12, 10)
        contacts_layout.setSpacing(6)

        head = QLabel("📞  معلومات التواصل")
        head.setObjectName("cardTitle")
        contacts_layout.addWidget(head)

        contacts_layout.addWidget(ContactRow(
            "📱", "الهاتف", "+963 991 758 886", "tel:+963991758886"))
        contacts_layout.addWidget(ContactRow(
            "💬", "واتساب", "+963 991 758 886", "https://wa.me/963991758886"))
        contacts_layout.addWidget(ContactRow(
            "✉️", "البريد الإلكتروني", "ahmadalfarahat099175@gmail.com",
            "mailto:ahmadalfarahat099175@gmail.com"))

        layout.addWidget(contacts)

        # ===== حقوق النشر =====
        copyright = QLabel("© 2026 المهندس أحمد مصطفى الفرحات — جميع الحقوق محفوظة")
        copyright.setObjectName("copyrightLabel")
        copyright.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright)

        layout.addStretch()
