import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QFrame, QPushButton, QApplication,
    QMessageBox,
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

from ui import i18n
from ui.i18n import tr
from ui.compress_tab import CompressTab
from ui.split_tab import SplitTab
from ui.merge_tab import MergeTab
from ui.convert_tab import ConvertTab
from ui.archive_tab import ArchiveTab
from ui.pdf2img_tab import Pdf2ImgTab
from ui.extract_tab import ExtractTab
from ui.export_tab import ExportTab
from ui.diff_tab import DiffTab
from ui.pages_tab import PagesTab
from ui.stamp_tab import StampTab
from ui.protect_tab import ProtectTab
from ui.ocr_tab import OcrTab
from ui.repair_tab import RepairTab
from ui.ai_tab import AiTab
from ui.info_tab import InfoTab
from ui.developer_tab import DeveloperTab
from ui.styles import get_style
from version import APP_VERSION


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app_title"))
        self.resize(1040, 760)
        self.setMinimumSize(880, 620)
        self.setLayoutDirection(Qt.RightToLeft if i18n.rtl() else Qt.LeftToRight)
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
        self._install_shortcuts()

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
        if self.theme_setting == "auto":
            return tr("theme_auto").format(mode="داكن" if self._resolved == "dark" else "فاتح")
        return tr("theme_dark") if self.theme_setting == "dark" else tr("theme_light")

    def _update_theme_btn(self):
        self.theme_btn.setText(self._theme_label())
        self.theme_btn.setToolTip("تبديل الثيم" if i18n.rtl() else "Switch theme")

    def _refresh_theme_widgets(self):
        """يعيد تلوين البطاقات والرسوم التي تخزن حالتها محلياً"""
        chart = getattr(self, "compress_tab", None)
        if chart:
            try:
                chart.refresh_theme()
            except AttributeError:
                pass

    # ---------- اللغة ----------
    def _toggle_language(self):
        new_lang = "en" if i18n.lang() == "ar" else "ar"
        i18n.set_lang(new_lang)
        box = QMessageBox(self)
        box.setWindowTitle("اللغة / Language")
        box.setText(tr("lang_switch_msg"))
        restart = box.addButton(tr("restart_now"), QMessageBox.AcceptRole)
        box.addButton(tr("later"), QMessageBox.RejectRole)
        box.exec()
        if box.clickedButton() is restart:
            from main import restart_app
            restart_app()

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
        app_title = QLabel(tr("app_name"))
        app_title.setObjectName("appTitle")
        app_subtitle = QLabel(tr("app_subtitle"))
        app_subtitle.setObjectName("appSubtitle")
        titles.addWidget(app_title)
        titles.addWidget(app_subtitle)

        header_row.addWidget(logo)
        header_row.addLayout(titles, 1)

        # --- أزرار التذييل ---
        self.theme_btn = QPushButton(self._theme_label())
        self.theme_btn.setObjectName("sidebarBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._cycle_theme)

        self.lang_btn = QPushButton(tr("lang_btn"))
        self.lang_btn.setObjectName("sidebarBtn")
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.clicked.connect(self._toggle_language)

        # --- عناصر القائمة (بأقسام) ---
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        self.sidebar.setVerticalScrollMode(QListWidget.ScrollPerPixel)

        sections = {
            "sec_core": ["compress", "split", "merge", "convert"],
            "sec_convert": ["pdf2img", "extract", "export", "ocr"],
            "sec_edit": ["pages", "stamp", "protect", "repair"],
            "sec_extra": ["diff", "ai", "archive"],
            "sec_system": ["info", "developer"],
        }
        labels = {
            "compress": tr("t_compress"), "split": tr("t_split"),
            "merge": tr("t_merge"), "convert": tr("t_convert"),
            "pdf2img": tr("t_pdf2img"), "extract": tr("t_extract"),
            "export": tr("t_export"), "ocr": tr("t_ocr"),
            "pages": tr("t_pages"),
            "stamp": tr("t_stamp"), "protect": tr("t_protect"),
            "repair": tr("t_repair"), "diff": tr("t_diff"),
            "ai": tr("t_ai"), "archive": tr("t_archive"),
            "info": tr("t_info"), "developer": tr("t_developer"),
        }
        self._tool_rows: dict[str, int] = {}
        for sec_key, tool_keys in sections.items():
            sec_item = QListWidgetItem()
            sec_item.setFlags(Qt.NoItemFlags)
            sec_item.setSizeHint(QSize(0, 38))
            self.sidebar.addItem(sec_item)
            sec_label = QLabel(tr(sec_key))
            sec_label.setObjectName("sidebarSection")
            sec_label.setAlignment(Qt.AlignCenter)
            sec_label.setMinimumHeight(38)  # ضروري: يمنع انهيار ارتفاع الـwidget داخل الصف
            self.sidebar.setItemWidget(sec_item, sec_label)

            for key in tool_keys:
                item = QListWidgetItem(labels[key])
                item.setData(Qt.UserRole, key)
                item.setSizeHint(QSize(0, 44))
                self.sidebar.addItem(item)
                self._tool_rows[key] = self.sidebar.row(item)

        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)

        # --- التذييل (الثيم + اللغة + النسخة) ---
        footer_widget = QWidget()
        footer_widget.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(12, 12, 12, 14)
        footer_layout.setSpacing(8)

        footer_buttons = QHBoxLayout()
        footer_buttons.setSpacing(8)
        footer_buttons.addWidget(self.theme_btn, 1)
        footer_buttons.addWidget(self.lang_btn)

        footer_layout.addLayout(footer_buttons)

        footer = QLabel(f"v{APP_VERSION}  •  MIT License")
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
        self.pdf2img_tab = Pdf2ImgTab()
        self.extract_tab = ExtractTab()
        self.export_tab = ExportTab()
        self.diff_tab = DiffTab()
        self.pages_tab = PagesTab()
        self.stamp_tab = StampTab()
        self.protect_tab = ProtectTab()
        self.ocr_tab = OcrTab()
        self.repair_tab = RepairTab()
        self.ai_tab = AiTab()
        self.info_tab = InfoTab()
        self.developer_tab = DeveloperTab()

        tabs = [
            self.compress_tab, self.split_tab, self.merge_tab, self.convert_tab,
            self.pdf2img_tab, self.extract_tab, self.export_tab, self.ocr_tab,
            self.pages_tab, self.stamp_tab, self.protect_tab, self.repair_tab,
            self.diff_tab, self.ai_tab, self.archive_tab,
            self.info_tab, self.developer_tab,
        ]
        # ترتيب التبويبات في الـstack — مفتاح الأداة → فهرس الصفحة
        tab_keys = ["compress", "split", "merge", "convert", "pdf2img", "extract",
                    "export", "ocr", "pages", "stamp", "protect", "repair",
                    "diff", "ai", "archive", "info", "developer"]
        self._tab_index = {k: i for i, k in enumerate(tab_keys)}
        for tab in tabs:
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

        self.sidebar.setCurrentRow(self._tool_rows["compress"])
        self._update_theme_btn()

    # ---------- اختصارات ولوحة الأوامر ----------
    def _install_shortcuts(self):
        """اختصارات لوحة المفاتيح: Ctrl+1..9,0 للأدوات الأولى وCtrl+K للبحث."""
        keys_order = ["compress", "split", "merge", "convert", "pdf2img",
                      "extract", "export", "ocr", "pages", "stamp"]
        for n, key in enumerate(keys_order, start=1):
            seq = str(n) if n <= 9 else "0"
            sc = QShortcut(QKeySequence(f"Ctrl+{seq}"), self)
            sc.activated.connect(lambda k=key: self.jump_to(k))

        palette_sc = QShortcut(QKeySequence("Ctrl+K"), self)
        palette_sc.activated.connect(self._open_palette)

        self._update_shortcut = QShortcut(QKeySequence("F5"), self)
        self._update_shortcut.activated.connect(self._manual_update_check)

    def _open_palette(self):
        from ui.palette import CommandPalette
        labels = {
            "compress": tr("t_compress"), "split": tr("t_split"),
            "merge": tr("t_merge"), "convert": tr("t_convert"),
            "pdf2img": tr("t_pdf2img"), "extract": tr("t_extract"),
            "export": tr("t_export"), "ocr": tr("t_ocr"),
            "pages": tr("t_pages"),
            "stamp": tr("t_stamp"), "protect": tr("t_protect"),
            "repair": tr("t_repair"), "diff": tr("t_diff"),
            "ai": tr("t_ai"), "archive": tr("t_archive"),
            "info": tr("t_info"), "developer": tr("t_developer"),
        }
        actions = [(labels[k], k) for k in self._tool_rows]
        actions.append(("🎨 " + tr("theme_dark"), "__theme__"))
        actions.append(("🌐 " + tr("lang_btn"), "__lang__"))
        palette = CommandPalette(actions, self)
        palette.jump_callback = self._palette_jump
        palette.exec()

    def _palette_jump(self, key: str):
        if key == "__theme__":
            self._cycle_theme()
        elif key == "__lang__":
            self._toggle_language()
        else:
            self.jump_to(key)

    def jump_to(self, key: str):
        """ينتقل إلى أداة عبر مفتاحها (يُستخدم من الاختصارات واللوحة)."""
        row = self._tool_rows.get(key)
        if row is not None:
            self.sidebar.setCurrentRow(row)

    # ---------- فاحص التحديث ----------
    def _manual_update_check(self):
        from ui.update_checker import check_for_update
        check_for_update(self, notify_uptodate=True)

    def _auto_update_check(self):
        """فحص هادئ عند الإقلاع — نافذة فقط إذا وُجد إصدار أحدث."""
        from ui.update_checker import check_for_update
        check_for_update(self, notify_uptodate=False)

    # ---------- التنقل ----------
    def _on_sidebar_changed(self, row):
        """ينتقل إلى التبويب المرتبط بالصف — صفوف الأقسام (بلا مفتاح) تُتجاهل."""
        item = self.sidebar.item(row)
        key = item.data(Qt.UserRole) if item else None
        if key and key in self._tab_index:
            self.stack.setCurrentIndex(self._tab_index[key])

    def closeEvent(self, event):
        """يُغلِق خيط فاحص التحديث قبل إغلاق النافذة."""
        try:
            from ui.update_checker import close as close_update_executor
            close_update_executor()
        except Exception:
            pass
        super().closeEvent(event)
