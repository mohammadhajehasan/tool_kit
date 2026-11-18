"""فاحص التحديث — يقارن إصدار التطبيق مع آخر إصدار منشور على GitHub."""

import json
import urllib.request

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from version import APP_VERSION, RELEASES_URL, LATEST_API
from ui.i18n import tr


def fetch_latest(timeout: float = 6.0) -> tuple[str, str]:
    """يجلب وسم وآخر إصدار من GitHub. يرمي استثناء عند الفشل."""
    req = urllib.request.Request(
        LATEST_API,
        headers={"User-Agent": "pdf-toolbox-app",
                 "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    tag = (data.get("tag_name") or "").lstrip("v")
    url = data.get("html_url") or RELEASES_URL
    return tag, url


def is_newer(latest: str, current: str) -> bool:
    def parts(s: str) -> tuple[int, ...]:
        return tuple(int(p) for p in s.split(".") if p.isdigit())

    try:
        return parts(latest) > parts(current)
    except Exception:
        return False


def _show_dialog(parent, latest: str, url: str):
    dlg = QDialog(parent)
    dlg.setWindowTitle(tr("update_title"))
    dlg.setModal(True)
    dlg.setMinimumWidth(420)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(24, 22, 24, 20)
    layout.setSpacing(12)

    head = QLabel(f"🔔  {tr('update_title')}")
    head.setObjectName("cardTitle")
    body = QLabel(tr("update_body").format(latest=latest, current=APP_VERSION))
    body.setObjectName("cardBody")
    body.setWordWrap(True)

    buttons = QHBoxLayout()
    download = QPushButton(tr("update_btn"))
    download.setObjectName("primaryBtn")
    download.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
    later = QPushButton(tr("update_later"))
    later.setObjectName("secondaryBtn")
    later.clicked.connect(dlg.reject)
    buttons.addStretch()
    buttons.addWidget(later)
    buttons.addWidget(download)

    layout.addWidget(head)
    layout.addWidget(body)
    layout.addLayout(buttons)

    from ui.styles import current_theme
    dlg.setStyleSheet(get_app_style())
    dlg.exec()


def get_app_style():
    """ورقة الأنماط النشطة (تُطبق على الحوار حتى يتبع الثيم)."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    return app.styleSheet() if app else ""


def check_for_update(parent=None, notify_uptodate: bool = False):
    """
    يفحص التحديث في خيط منفصل (لا يجمّد الواجهة).
    notify_uptodate=True يعرض رسالة حتى لو كان الإصدار أحدث (فحص يدوي).
    """
    from ui.toast import show_toast
    from ui.widgets import Worker

    def on_ok(result):
        tag, url = result
        if is_newer(tag, APP_VERSION):
            _show_dialog(parent, tag, url)
        elif notify_uptodate and parent is not None:
            show_toast(parent, tr("uptodate"), "info")

    def on_fail(_err):
        if notify_uptodate and parent is not None:
            show_toast(parent, "تعذر الاتصال بالإنترنت — تأكد من اتصالك ثم أعد المحاولة", "warning")

    worker = Worker(fetch_latest)
    worker.finished_ok.connect(on_ok)
    worker.failed.connect(on_fail)
    worker.start()
    return worker
