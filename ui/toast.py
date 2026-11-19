"""إشعارات عائمة (Toast) — تظهر لثوانٍ ثم تختفي بدون حجب الواجهة."""

from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect, QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint

from ui.i18n import rtl, tr_text


class Toast(QLabel):
    def __init__(self, parent: QWidget, message: str, kind: str = "info", duration_ms: int = 3200):
        super().__init__(message, parent)
        self.setObjectName("toastNotification")
        self.setProperty("kind", kind)
        self.setWordWrap(True)
        self.setAlignment((Qt.AlignRight if rtl() else Qt.AlignLeft) | Qt.AlignVCenter)
        self.setMargin(14)
        self.setMinimumWidth(260)
        self.setMaximumWidth(420)
        self.adjustSize()

        colors = {
            "success": ("#166534", "#F0FDF4", "#86EFAC"),
            "error": ("#B91C1C", "#FEF2F2", "#FCA5A5"),
            "info": ("#1E3A8A", "#EFF6FF", "#93C5FD"),
            "warning": ("#92400E", "#FFFBEB", "#FCD34D"),
        }
        fg, bg, border = colors.get(kind, colors["info"])
        self.setStyleSheet(
            f"QLabel#toastNotification {{"
            f"  color: {fg}; background: {bg}; border: 1px solid {border};"
            f"  border-radius: 12px; padding: 12px 16px; font-size: 13px; font-weight: 600;"
            f"}}"
        )

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

        parent_rect = parent.rect()
        x = parent_rect.width() - self.width() - 28
        y = parent_rect.height() - self.height() - 28
        self.move(max(16, x), max(16, y))
        self.show()
        self.raise_()

        self._fade_in = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade_in.setDuration(220)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_in.start()

        QTimer.singleShot(duration_ms, self._fade_out)

    def _fade_out(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(280)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(self.deleteLater)
        anim.start()
        self._fade_out_anim = anim  # منع جمع القمامة


def show_toast(parent: QWidget, message: str, kind: str = "info", duration_ms: int = 3200):
    """يعرض إشعاراً عائماً فوق النافذة الأب."""
    if parent is None:
        return None
    # استخدم النافذة الرئيسية إن أمكن لتثبيت الموقع
    host = parent.window() if hasattr(parent, "window") else parent
    return Toast(host, tr_text(message), kind=kind, duration_ms=duration_ms)
