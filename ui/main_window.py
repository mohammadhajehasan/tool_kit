from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QFrame, QPushButton, QApplication
)
from PySide6.QtCore import Qt, QSize

from ui.compress_tab import CompressTab
from ui.split_tab import SplitTab
from ui.merge_tab import MergeTab
from ui.convert_tab import ConvertTab
from ui.styles import get_style
from ui.gender_dialog import ask_gender


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolbox — أداة PDF")
        self.resize(1020, 700)
        self.setMinimumSize(860, 580)
        self.setLayoutDirection(Qt.RightToLeft)

        # اختيار الجنس وتطبيق اللون المناسب
        self.gender = ask_gender(self) or "male"
        self._apply_style()

        self._build_ui()

    def _apply_style(self):
        """يطبق الثيم على مستوى التطبيق بالكامل (وليس النافذة فقط)"""
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(get_style(self.gender))  # type: ignore[attr-defined]
        else:
            self.setStyleSheet(get_style(self.gender))

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ===== الشريط الجانبي =====
        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebarContainer")
        sidebar_container.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # --- الترويسة ---
        header = QWidget()
        header.setObjectName("sidebarHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        app_title = QLabel("  📄  أداة PDF")
        app_title.setObjectName("appTitle")
        app_title.setAlignment(Qt.AlignCenter)

        app_subtitle = QLabel("كل أدوات PDF في مكان واحد")
        app_subtitle.setObjectName("appSubtitle")
        app_subtitle.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(app_title)
        header_layout.addWidget(app_subtitle)

        # خط فاصل رفيع
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255,255,255,0.08);")

        # --- زر تغيير الثيم (في أعلى الشريط الجانبي) ---
        self.theme_btn = QPushButton("🎨  تغيير الثيم")
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setToolTip("تغيير لون التطبيق (بنفسجي / وردي)")
        self.theme_btn.clicked.connect(self._prompt_switch_gender)
        sidebar_layout.addWidget(self.theme_btn)

        # --- عناصر القائمة ---
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFocusPolicy(Qt.NoFocus)

        items = [
            ("🗜️   ضغط PDF", "compress"),
            ("✂️   تقطيع PDF", "split"),
            ("🔗   دمج PDF", "merge"),
            ("🖼️   صور إلى PDF", "convert"),
        ]
        for text, key in items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            item.setSizeHint(QSize(0, 50))
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)

        # --- التذييل (نسخة + زر تبديل النوع/الثيم) ---
        footer_widget = QWidget()
        footer_widget.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(12, 8, 12, 12)
        footer_layout.setSpacing(6)

        self.gender_btn = QPushButton("🎨  تغيير النوع / الثيم")
        self.gender_btn.setObjectName("sidebarBtn")
        self.gender_btn.setCursor(Qt.PointingHandCursor)
        self.gender_btn.clicked.connect(self._prompt_switch_gender)
        footer_layout.addWidget(self.gender_btn)

        footer = QLabel("v1.0  •  MIT License")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #475569; font-size: 11px; padding: 4px; font-weight: 400; background-color: #0f172a;")
        footer_layout.addWidget(footer)

        sidebar_layout.addWidget(header)
        sidebar_layout.addWidget(separator)
        sidebar_layout.addWidget(self.sidebar, 1)
        sidebar_layout.addWidget(footer_widget)

        # ===== منطقة المحتوى =====
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.compress_tab = CompressTab()
        self.split_tab = SplitTab()
        self.merge_tab = MergeTab()
        self.convert_tab = ConvertTab()

        for tab in (self.compress_tab, self.split_tab, self.merge_tab, self.convert_tab):
            wrapper = QWidget()
            wrapper.setObjectName("pageContainer")
            wrapper_layout = QVBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(36, 32, 36, 32)
            wrapper_layout.addWidget(tab)
            self.stack.addWidget(wrapper)

        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.addWidget(self.stack)

        root_layout.addWidget(sidebar_container)
        root_layout.addWidget(content_area, 1)

        self.sidebar.setCurrentRow(0)

    def _prompt_switch_gender(self):
        """يعرض حوار اختيار الجنس مجدداً لتغيير النوع/الثيم أثناء التشغيل."""
        new_gender = ask_gender(self) or self.gender
        if new_gender != self.gender:
            self.gender = new_gender
            self._apply_style()

    def _on_sidebar_changed(self, index):
        self.stack.setCurrentIndex(index)