import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QProgressBar, QFileDialog, QButtonGroup, QRadioButton, QSizePolicy, QCheckBox
)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen

from ui.widgets import DropZone, Worker, CancellationToken
from ui.styles import chart_colors
from ui.toast import show_toast
from core.compress import compress_pdf, estimate_size, format_size, ghostscript_available
from core.history import record


class OptionCard(QFrame):
    """بطاقة اختيار مستوى الضغط — تصميم عصري"""

    def __init__(self, title, desc, value, group: QButtonGroup, checked=False, parent=None):
        super().__init__(parent)
        self.setObjectName("optionCard")
        self.value = value
        self.setProperty("selected", checked)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        self.radio = QRadioButton()
        self.radio.setChecked(checked)
        group.addButton(self.radio)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("optionTitle")
        d = QLabel(desc)
        d.setObjectName("optionDesc")
        d.setWordWrap(True)
        text_box.addWidget(t)
        text_box.addWidget(d)

        layout.addWidget(self.radio)
        layout.addLayout(text_box, 1)

        self.radio.toggled.connect(self._on_toggle)

    def _on_toggle(self, checked):
        self.setProperty("selected", checked)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        self.radio.setChecked(True)
        super().mousePressEvent(event)


class CompressChart(QWidget):
    """رسم شريطي خفيف عبر QPainter — بديل عن matplotlib."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setMaximumHeight(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setVisible(False)
        self._last = None  # (orig_bytes, comp_bytes)

    def update_chart(self, original_bytes: int, compressed_bytes: int):
        self._last = (original_bytes, compressed_bytes)
        self.setVisible(True)
        self.update()

    def refresh_theme(self):
        if self._last:
            self.update_chart(*self._last)
        elif self.isVisible():
            self.setVisible(False)

    def paintEvent(self, event):
        if not self._last:
            return
        orig, comp = self._last
        cc = chart_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        margin_l, margin_r, margin_t, margin_b = 100, 80, 16, 28
        chart_w = w - margin_l - margin_r
        bar_h = 28
        gap = 22
        max_val = max(orig, comp, 1)

        rows = [
            ("قبل الضغط", orig, QColor(cc["before"])),
            ("بعد الضغط", comp, QColor(cc["after"])),
        ]
        y0 = margin_t
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        for i, (label, value, color) in enumerate(rows):
            y = y0 + i * (bar_h + gap)
            painter.setPen(QColor(cc["text"]))
            painter.drawText(QRectF(8, y, margin_l - 16, bar_h), Qt.AlignVCenter | Qt.AlignRight, label)

            bar_w = max(4.0, (value / max_val) * chart_w)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(margin_l, y, bar_w, bar_h), 8, 8)

            size_mb = value / (1024 * 1024)
            text = f"{size_mb:.2f} MB" if size_mb >= 0.01 else f"{size_mb * 1024:.0f} KB"
            painter.setPen(QColor(cc["text"]))
            painter.drawText(
                QRectF(margin_l + bar_w + 8, y, margin_r - 12, bar_h),
                Qt.AlignVCenter | Qt.AlignLeft,
                text,
            )

        # محور سفلي بسيط
        painter.setPen(QPen(QColor(cc["spine"]), 1))
        baseline = y0 + 2 * (bar_h + gap) - gap + 4
        painter.drawLine(margin_l, baseline, margin_l + chart_w, baseline)
        painter.setPen(QColor(cc["axis_label"]))
        small = QFont()
        small.setPointSize(9)
        painter.setFont(small)
        painter.drawText(
            QRectF(margin_l, baseline + 2, chart_w, 20),
            Qt.AlignCenter,
            "الحجم (MB)",
        )
        painter.end()


class CompressTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("ضغط ملفات PDF")
        title.setObjectName("pageTitle")
        desc = QLabel("قلّل حجم ملف PDF مع الحفاظ على المحتوى قابلاً للقراءة")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            sub_text="يدعم ملف واحد في كل مرة",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file_selected)
        layout.addWidget(self.drop_zone)

        self.file_label = QLabel("")
        self.file_label.setObjectName("fileMeta")
        layout.addWidget(self.file_label)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)
        self.button_group = QButtonGroup(self)

        self.light_card = OptionCard(
            "ضغط خفيف",
            "أقل تدخّل ممكن — يحافظ على أعلى جودة ويقلّل الحجم قليلاً",
            "light",
            self.button_group,
        )
        self.recommended_card = OptionCard(
            "الضغط الموصى به",
            "يقلّص حجم الملف إلى النصف تقريباً مع الحفاظ على جودة جيدة",
            "recommended",
            self.button_group,
            checked=True,
        )
        self.extreme_card = OptionCard(
            "الضغط الشديد",
            "أقصى تقليص ممكن للحجم، قد يؤثر على جودة الصور والخطوط",
            "extreme",
            self.button_group,
        )
        options_layout.addWidget(self.light_card)
        options_layout.addWidget(self.recommended_card)
        options_layout.addWidget(self.extreme_card)
        layout.addLayout(options_layout)

        self.gs_check = QCheckBox("استخدام Ghostscript لضغط أقوى (اختياري)")
        self.gs_available = ghostscript_available()
        if self.gs_available:
            self.gs_check.setToolTip(
                "يستخدم محرك Ghostscript للضغط، مع تحقق تلقائي من سلامة الملف قبل الحفظ"
            )
        else:
            self.gs_check.setEnabled(False)
            self.gs_check.setToolTip(
                "Ghostscript غير مثبّت على هذا الجهاز.\n"
                "سيتم استخدام PyMuPDF للضغط (فعّال أيضاً).\n"
                "لتفعيله: ثبّت Ghostscript أو ضع gswin64c.exe في resources/gs/"
            )
        layout.addWidget(self.gs_check)

        run_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        self.estimate_btn = QPushButton("📏 تقدير الحجم")
        self.estimate_btn.setObjectName("secondaryBtn")
        self.estimate_btn.setEnabled(False)
        self.estimate_btn.clicked.connect(self._run_estimate)
        self.run_btn = QPushButton("ضغط الملف")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run_compress)
        run_layout.addStretch()
        run_layout.addWidget(self.estimate_btn)
        run_layout.addWidget(self.cancel_btn)
        run_layout.addWidget(self.run_btn)
        layout.addLayout(run_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.chart = CompressChart(self)
        layout.addWidget(self.chart)

        layout.addStretch()

    def refresh_theme(self):
        self.chart.refresh_theme()

    def _on_file_selected(self, paths):
        if not paths:
            return
        path = paths[0]
        if not path.lower().endswith(".pdf"):
            show_toast(self, "الرجاء اختيار ملف PDF فقط", "warning")
            return
        self.selected_file = path
        size = format_size(os.path.getsize(path))
        self.file_label.setText(f"📄 {os.path.basename(path)}  ({size})")
        self.run_btn.setEnabled(True)
        self.estimate_btn.setEnabled(True)
        self.status_label.setText("")
        self.chart.setVisible(False)

    def _cancel(self):
        if self.worker:
            self.worker.cancel()

    def _selected_level(self) -> str:
        for card in (self.light_card, self.recommended_card, self.extreme_card):
            if card.radio.isChecked():
                return card.value
        return "recommended"

    def _run_estimate(self):
        """تقدير سريع للحجم بعد الضغط دون حفظ الملف."""
        if not self.selected_file or self.worker:
            return
        level = self._selected_level()
        self.estimate_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("⏳ جارٍ تقدير الحجم (تجربة الضغط على نسخة مؤقتة)…")
        self.worker = Worker(estimate_size, self.selected_file, level)
        self.worker.finished_ok.connect(self._on_estimate)
        self.worker.failed.connect(self._on_failure)
        self.worker.start()

    def _on_estimate(self, result):
        self.worker = None
        self.progress.setVisible(False)
        self.estimate_btn.setEnabled(True)
        orig = format_size(result["original_size"])
        est = format_size(result["compressed_size"])
        pct = result["reduction_percent"]
        self.status_label.setText(
            f"📏 تقدير المستوى المحدد:  {orig} ← {est}  (توفير {pct}%)\n"
            "انقر «ضغط الملف» للحفظ الفعلي")
        self.status_label.setObjectName("")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)

    def _run_compress(self):
        if not self.selected_file:
            return

        level = self._selected_level()
        use_gs = self.gs_check.isChecked()

        suggested_name = os.path.splitext(os.path.basename(self.selected_file))[0] + "_مضغوط.pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ الملف المضغوط", suggested_name, "PDF Files (*.pdf)"
        )
        if not output_path:
            return

        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.status_label.setText("⏳  جاري الضغط... يرجى الانتظار")
        self.status_label.setObjectName("")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        self.chart.setVisible(False)

        token = CancellationToken()
        self.worker = Worker(
            compress_pdf, self.selected_file, output_path,
            level=level, use_ghostscript=use_gs, cancel_token=token,
        )
        self.worker.finished_ok.connect(lambda res: self._on_success(res, output_path))
        self.worker.failed.connect(self._on_failure)
        self.worker.start()

    def _on_success(self, result, output_path):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        orig = format_size(result["original_size"])
        comp = format_size(result["compressed_size"])
        pct = result["reduction_percent"]
        method = result.get("method", "غير معروف")

        if pct > 0:
            pct_text = f"تم توفير {pct}% من الحجم"
            emoji = "✅"
            style = "statusSuccess"
        else:
            pct_text = "الملف مضغوط أصلاً — لم يتغيّر الحجم كثيراً"
            emoji = "ℹ️"
            style = "statusSuccess"

        self.status_label.setObjectName(style)
        self.status_label.setText(
            f"{emoji}  تم الضغط بنجاح عبر {method}\n\n"
            f"    📊  الحجم الأصلي:    {orig}\n"
            f"    📊  الحجم الجديد:    {comp}\n"
            f"    📉  {pct_text}\n\n"
            f"    💾  حُفظ في:  {output_path}"
        )
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        self.chart.update_chart(result["original_size"], result["compressed_size"])
        show_toast(self, f"تم الضغط عبر {method} — توفير {pct}%", "success")
        try:
            record("ضغط PDF", output_path, saved_bytes=result["original_size"] - result["compressed_size"])
        except Exception:
            pass

    def _on_failure(self, error_msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setObjectName("statusError")
        self.status_label.setText(f"❌  فشلت العملية:\n{error_msg}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        self.chart.setVisible(False)
        show_toast(self, error_msg, "error")
