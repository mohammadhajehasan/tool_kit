"""فاحص التحديث — يقارن إصدار التطبيق مع آخر إصدار منشور على GitHub."""

import json
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QObject, Signal, QTimer
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from version import APP_VERSION, RELEASES_URL, LATEST_API
from ui.i18n import tr


def fetch_latest(timeout: float = 6.0) -> tuple[str, str]:
    """يجلب وسم وآخر إصدار من GitHub. يرمي استثناء عند الفشل."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        LATEST_API,
        headers={
            "User-Agent": "pdf-toolbox-app",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
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

    head = QLabel(f"\U0001f514  {tr('update_title')}")
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

    # اتبع الثيم النشط للتطبيق
    app = QApplication.instance()
    if app is not None:
        dlg.setStyleSheet(app.styleSheet() or "")
    dlg.exec()


class _UpdateSignals(QObject):
    """وسيط لإعادة نتيجة الفحص من خيط الخلفية إلى الخيط الرئيسي بأمان."""
    got_update = Signal(str, str)   # tag, url
    failed = Signal()


# خيط Python خلفي واحد مشترك — يُعاد تشغيله كل طلب جديد بآمان
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="update_fetcher")
_signals = _UpdateSignals()


def close():
    """يُغلِق خيط الفحص الخلفي (يُدعى من MainWindow.closeEvent)."""
    _EXECUTOR.shutdown(wait=False, cancel_futures=True)


def check_for_update(parent=None, notify_uptodate: bool = False):
    """
    يفحص التحديث في خيط خلفي ثم يعرض النتيجة في الخيط الرئيسي عبر إشارة queued.
    notify_uptodate=True يعرض رسالة حتى لو كان الإصدار أحدث (فحص يدوي).
    """
    from ui.toast import show_toast

    def on_ok(tag: str, url: str):
        if is_newer(tag, APP_VERSION):
            # نستخدم singleShot(0) لنضمن أن عرض الحوار يعود للخيط الرئيسي
            # مباشرة بعد انتهاء هذه الدالة، ما يمنع تشابك حلقات الأحداث.
            QTimer.singleShot(0, lambda: _show_dialog(parent, tag, url))
        elif notify_uptodate and parent is not None:
            show_toast(parent, tr("uptodate"), "info")

    def on_fail():
        if notify_uptodate and parent is not None:
            show_toast(parent, "تعذر الاتصال بالإنترنت — تأكد من اتصالك ثم أعد المحاولة", "warning")

    # افصل أي اتصال سابق كي لا تتراكم الإشارات عند تكرار الفحص
    try:
        _signals.got_update.disconnect()
    except Exception:
        pass
    try:
        _signals.failed.disconnect()
    except Exception:
        pass
    _signals.got_update.connect(on_ok, Qt.ConnectionType.QueuedConnection)
    _signals.failed.connect(on_fail, Qt.ConnectionType.QueuedConnection)

    def _fetch_and_emit():
        try:
            tag, url = fetch_latest()
            _signals.got_update.emit(tag, url)
        except Exception:
            _signals.failed.emit()

    _EXECUTOR.submit(_fetch_and_emit)
