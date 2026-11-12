from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QFrame, QPushButton, QApplication,
)
from PySide6.QtCore import Qt, QSize
import os

from ui.compress_tab import CompressTab
from ui.split_tab import SplitTab
from ui.merge_tab import MergeTab
from ui.convert_tab import ConvertTab
from ui.archive_tab import ArchiveTab
from ui.info_tab import InfoTab
from ui.developer_tab import DeveloperTab
from ui.styles import get_style


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolbox — أداة PDF")
        self.resize(1040, 720)
        self.setMinimumSize(880, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self._load_icon()

        # الثيم من الإعدادات المحفوظة (auto/dark/light)
        self.theme_setting = "auto"
        try:
            import json
            spath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settings.json")
            if os.path.exists(spath):
                with open(spath, "r", encoding="utf-8") as f:
                    saved = json.load(f).get("theme", "auto")
                if saved in ("auto", "dark", "light"):
                    self.theme_setting = saved
        except Exception:
            pass
        self._resolved = None
        self._apply_style()

        self._build_ui()

    def _load_icon(self):
        """يحمّل أيقونة التطبيق إن وُجدت"""
        from pathlib import Path
        for name in ("app.ico", "app.png", "icon.png", "app.icns"):
            p = Path(__file__).parent.parent / "resources" / name
            if p.exists():
                from PySide6.QtGui import QIcon
                self.setWindowIcon(QIcon(str(p)))
                break

    # ---------- الثيمات ----------
    def _detect_system_theme(self) -> str:
        """يحل الثيم التلقائي من ثيم نظام التشغيل"""
        try:
            hints = QApplication.styleHints()
            scheme = getattr(hints, "colorScheme", lambda: None)()
            if scheme is not None:
                return "dark" if scheme == Qt.ColorScheme.Dark else "light"
        except Exception:
            pass
        return "light"

    def _apply_style(self):
        """يطبق نظام التصميم الموحد (styles.py) على مستوى التطبيق بالكامل"""
        resolved = {
            "auto": self._detect_system_theme(),
            "dark": "dark",
            "light": "light",
        }[self.theme_setting]
        self._resolved = resolved
        app = QApplication.instance()
        stylesheet = get_style(resolved)
        if app is not None:
            app.setStyleSheet(stylesheet)
        else:
            self.setStyleSheet(stylesheet)

    def _cycle_theme(self):
        """auto → dark → light → auto (مع الحفظ)"""
        order = ["auto", "dark", "light"]
        self.theme_setting = order[(order.index(self.theme_setting) + 1) % 3]
        self._apply_style()
        self._update_theme_btn()
        self._persist_theme()
        self._refresh_theme_widgets()

    def _persist_theme(self):
        """يحفظ اختيار الثيم حتى يعود التطبيق بنفس الوضع لاحقاً"""
        try:
            import json
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settings.json")
            data = {}
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data["theme"] = self.theme_setting
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # الحفظ الاختياري — لا نمنع التطبيق من العمل

    def _theme_label(self) -> str:
        return {
            "auto": f"⚙️ تلقائي ({'داكن' if self._resolved == 'dark' else 'فاتح'})",
            "dark": "🌙 داكن",
            "light": "☀️ فاتح",
        }.get(self.theme_setting, "🎨 الثيم")

    def _update_theme_btn(self):
        self.theme_btn.setText(self._theme_label())
        self.theme_btn.setToolTip(
            { "auto": "يتبع ثيم نظام التشغيل — انقر للتغيير",
              "dark": "الوضع الداكن — انقر للتبديل",
              "light": "الوضع الفاتح — انقر للتبديل" }[self.theme_setting]
        )

    def _refresh_theme_widgets(self):
        """يعيد تلوين البطاقات والرسوم التي تخزن حالتها محلياً"""
        from ui.compress_tab import CompressChart
        chart = getattr(self, "compress_tab", None)
        if chart:
            try:
                chart.refresh_theme()
            except AttributeError:
                pass

    # ---------- بناء الواجهة ----------
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
        sidebar_container.setFixedWidth(248)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # --- الترويسة: شعار + اسم ---
        header = QWidget()
        header.setObjectName("sidebarHeader")
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(18, 16, 10, 12)
        header_row.setSpacing(12)

        logo = QLabel("📄")
        logo.setObjectName("appLogo")
        logo.setAlignment(Qt.AlignCenter)

        titles = QVBoxLayout()
        titles.setSpacing(0)
        app_title = QLabel("أداة PDF")
        app_title.setObjectName("appTitle")
        app_subtitle = QLabel("كل الأدوات في مكان واحد")
        app_subtitle.setObjectName("appSubtitle")
        titles.addWidget(app_title)
        titles.addWidget(app_subtitle)

        header_row.addWidget(logo)
        header_row.addLayout(titles, 1)

        # --- زر تبديل الثيم (بجانب الترويسة) ---
        self.theme_btn = QPushButton(self._theme_label())
        self.theme_btn.setObjectName("sidebarBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._cycle_theme)
        self.theme_btn.setToolTip("تبديل الثيم")

        # --- عناصر القائمة ---
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFocusPolicy(Qt.NoFocus)

        items = [
            ("🗜️   ضغط PDF", "compress"),
            ("✂️   تقطيع PDF", "split"),
            ("🔗   دمج PDF", "merge"),
            ("🖼️   صور إلى PDF", "convert"),
            ("📦   فك ضغط", "archive"),
            ("ℹ️   معلومات", "info"),
            ("👨‍💻   المطور", "developer"),
        ]
        for text, key in items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            item.setSizeHint(QSize(0, 48))
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)

        # --- التذييل (زر الثيم + النسخة) ---
        footer_widget = QWidget()
        footer_widget.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(12, 12, 12, 14)
        footer_layout.setSpacing(8)

        footer_layout.addWidget(self.theme_btn)

        footer = QLabel("v1.2.0  •  MIT License")
        footer.setObjectName("versionLabel")
        footer.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(footer)

        sidebar_layout.addWidget(header)
        sidebar_layout.addWidget(self.sidebar, 1)
        sidebar_layout.addWidget(footer_widget)

        # ===== منطقة المحتوى =====
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.compress_tab = CompressTab()
        self.split_tab = SplitTab()
        self.merge_tab = MergeTab()
        self.convert_tab = ConvertTab()
        self.archive_tab = ArchiveTab()
        self.info_tab = InfoTab()
        self.developer_tab = DeveloperTab()

        for tab in (self.compress_tab, self.split_tab, self.merge_tab,
                    self.convert_tab, self.archive_tab,
                    self.info_tab, self.developer_tab):
            # تمرير داخلي عند ضيقة النافذة بدلاً من ضغط أو تداخل العناصر
            from PySide6.QtWidgets import QScrollArea
            scroll = QScrollArea()
            scroll.setObjectName("pageScroll")
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setFrameShape(QScrollArea.NoFrame)
            scroll.setWidget(tab)
            wrapper = QWidget()
            wrapper.setObjectName("pageContainer")
            wrapper_layout = QVBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(36, 30, 36, 30)
            wrapper_layout.addWidget(scroll)
            self.stack.addWidget(wrapper)

        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.stack)

        root_layout.addWidget(sidebar_container)
        root_layout.addWidget(content_area, 1)

        self.sidebar.setCurrentRow(0)
        self._update_theme_btn()

    def _on_sidebar_changed(self, index):
        self.stack.setCurrentIndex(index)
