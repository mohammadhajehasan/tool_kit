from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QPushButton, QApplication,
    QScrollArea, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
import os

from ui.compress_tab import CompressTab
from ui.split_tab import SplitTab
from ui.merge_tab import MergeTab
from ui.convert_tab import ConvertTab
from ui.pdf_to_images_tab import PdfToImagesTab
from ui.archive_tab import ArchiveTab
from ui.protect_tab import ProtectTab
from ui.watermark_tab import WatermarkTab
from ui.organize_tab import OrganizeTab
from ui.ocr_tab import OcrTab
from ui.export_tab import ExportTab
from ui.diff_tab import DiffTab
from ui.ai_tab import AiTab
from ui.info_tab import InfoTab
from ui.developer_tab import DeveloperTab
from ui.styles import get_style
from ui.icons import svg_icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolbox — أداة PDF")
        self.resize(1100, 740)
        self.setMinimumSize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)
        self._load_icon()

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
        self._fade_anim = None

        self._build_ui()

    def _load_icon(self):
        from pathlib import Path
        for name in ("app.ico", "app.png", "icon.png", "app.icns"):
            p = Path(__file__).parent.parent / "resources" / name
            if p.exists():
                from PySide6.QtGui import QIcon
                self.setWindowIcon(QIcon(str(p)))
                break

    def _detect_system_theme(self) -> str:
        try:
            hints = QApplication.styleHints()
            scheme = getattr(hints, "colorScheme", lambda: None)()
            if scheme is not None:
                return "dark" if scheme == Qt.ColorScheme.Dark else "light"
        except Exception:
            pass
        return "light"

    def _apply_style(self):
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
        order = ["auto", "dark", "light"]
        self.theme_setting = order[(order.index(self.theme_setting) + 1) % 3]
        self._apply_style()
        self._update_theme_btn()
        self._persist_theme()
        self._refresh_theme_widgets()
        self._refresh_sidebar_icons()

    def _persist_theme(self):
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
            pass

    def _theme_label(self) -> str:
        return {
            "auto": f"تلقائي ({'داكن' if self._resolved == 'dark' else 'فاتح'})",
            "dark": "داكن",
            "light": "فاتح",
        }.get(self.theme_setting, "الثيم")

    def _update_theme_btn(self):
        self.theme_btn.setText(self._theme_label())
        self.theme_btn.setToolTip(
            {"auto": "يتبع ثيم نظام التشغيل — انقر للتغيير",
             "dark": "الوضع الداكن — انقر للتبديل",
             "light": "الوضع الفاتح — انقر للتبديل"}[self.theme_setting]
        )

    def _refresh_theme_widgets(self):
        chart = getattr(self, "compress_tab", None)
        if chart:
            try:
                chart.refresh_theme()
            except AttributeError:
                pass

    def _icon_color(self) -> str:
        return "#C7D2FE" if self._resolved == "dark" else "#A3AEC8"

    def _refresh_sidebar_icons(self):
        color = self._icon_color()
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            key = item.data(Qt.UserRole)
            icon_name = self._nav_icon_map.get(key)
            if icon_name:
                item.setIcon(svg_icon(icon_name, color=color, size=18))

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebarContainer")
        sidebar_container.setFixedWidth(248)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("sidebarHeader")
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(18, 16, 10, 12)
        header_row.setSpacing(12)

        logo = QLabel()
        logo.setObjectName("appLogo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setPixmap(svg_icon("app", color="#A5B4FC", size=28).pixmap(28, 28))

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

        self.theme_btn = QPushButton(self._theme_label())
        self.theme_btn.setObjectName("sidebarBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._cycle_theme)
        self.theme_btn.setToolTip("تبديل الثيم")

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        self.sidebar.setIconSize(QSize(18, 18))

        self._nav_icon_map = {
            "compress": "compress",
            "split": "split",
            "merge": "merge",
            "convert": "images",
            "pdf_images": "pdf_images",
            "protect": "protect",
            "watermark": "watermark",
            "organize": "organize",
            "ocr": "ocr",
            "export": "export",
            "diff": "diff",
            "ai": "ai",
            "archive": "archive",
            "info": "info",
            "developer": "developer",
        }
        items = [
            ("ضغط PDF", "compress"),
            ("تقطيع PDF", "split"),
            ("دمج PDF", "merge"),
            ("صور إلى PDF", "convert"),
            ("PDF إلى صور", "pdf_images"),
            ("حماية وتشفير", "protect"),
            ("علامة مائية", "watermark"),
            ("تنظيم الصفحات", "organize"),
            ("OCR عربي", "ocr"),
            ("تصدير Word/Excel", "export"),
            ("مقارنة PDF", "diff"),
            ("مساعد ذكي", "ai"),
            ("فك ضغط", "archive"),
            ("معلومات", "info"),
            ("المطور", "developer"),
        ]
        color = self._icon_color()
        for text, key in items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            item.setSizeHint(QSize(0, 44))
            icon_name = self._nav_icon_map.get(key)
            if icon_name:
                item.setIcon(svg_icon(icon_name, color=color, size=18))
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)

        footer_widget = QWidget()
        footer_widget.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(12, 12, 12, 14)
        footer_layout.setSpacing(8)
        footer_layout.addWidget(self.theme_btn)

        footer = QLabel("v1.4.0  •  MIT License")
        footer.setObjectName("versionLabel")
        footer.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(footer)

        sidebar_layout.addWidget(header)
        sidebar_layout.addWidget(self.sidebar, 1)
        sidebar_layout.addWidget(footer_widget)

        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        self._stack_effect = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(self._stack_effect)
        self._stack_effect.setOpacity(1.0)

        self.compress_tab = CompressTab()
        self.split_tab = SplitTab()
        self.merge_tab = MergeTab()
        self.convert_tab = ConvertTab()
        self.pdf_images_tab = PdfToImagesTab()
        self.protect_tab = ProtectTab()
        self.watermark_tab = WatermarkTab()
        self.organize_tab = OrganizeTab()
        self.ocr_tab = OcrTab()
        self.export_tab = ExportTab()
        self.diff_tab = DiffTab()
        self.ai_tab = AiTab()
        self.archive_tab = ArchiveTab()
        self.info_tab = InfoTab()
        self.developer_tab = DeveloperTab()

        for tab in (
            self.compress_tab, self.split_tab, self.merge_tab,
            self.convert_tab, self.pdf_images_tab,
            self.protect_tab, self.watermark_tab, self.organize_tab,
            self.ocr_tab, self.export_tab, self.diff_tab, self.ai_tab,
            self.archive_tab, self.info_tab, self.developer_tab,
        ):
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
        if index < 0:
            return
        self.stack.setCurrentIndex(index)
        # تلاشي ناعم عند التنقل
        if self._fade_anim and self._fade_anim.state() == QPropertyAnimation.Running:
            self._fade_anim.stop()
        self._stack_effect.setOpacity(0.35)
        anim = QPropertyAnimation(self._stack_effect, b"opacity", self)
        anim.setDuration(180)
        anim.setStartValue(0.35)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._fade_anim = anim
