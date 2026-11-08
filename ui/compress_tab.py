import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QProgressBar, QFileDialog, QButtonGroup, QRadioButton, QMessageBox,
    QSizePolicy, QCheckBox
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("QtAgg")

from ui.widgets import DropZone, Worker
from ui.styles import chart_colors
from core.compress import compress_pdf, format_size, CompressError, ghostscript_available


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


class CompressChart(FigureCanvas):
    """رسم بياني شريطي يقارن حجم الملف قبل وبعد الضغط"""

    def __init__(self, parent=None, width=5, height=2.5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor("none")
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.22, right=0.82, top=0.88, bottom=0.38)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumHeight(200)
        self.setVisible(False)

    def update_chart(self, original_bytes: int, compressed_bytes: int):
        """يرسم رسم بياني شريطي يقارن الحجمين (متوافق مع الثيم النشط)"""
        self._last = (original_bytes, compressed_bytes)
        cc = chart_colors()

        self.axes.clear()
        self.setVisible(True)

        labels = ["  قبل الضغط  ", "  بعد الضغط  "]
        sizes_mb = [original_bytes / (1024 * 1024), compressed_bytes / (1024 * 1024)]
        colors = [cc["before"], cc["after"]]

        bars = self.axes.barh(labels, sizes_mb, color=colors, height=0.50,
                              edgecolor="white", linewidth=2)

        max_val = max(sizes_mb) if max(sizes_mb) > 0 else 1
        for bar, size in zip(bars, sizes_mb):
            text = f"{size:.2f} MB" if size >= 0.01 else f"{size * 1024:.0f} KB"
            x_pos = bar.get_width() + max_val * 0.04
            self.axes.text(
                x_pos, bar.get_y() + bar.get_height() / 2,
                text, va="center", ha="left",
                fontsize=11, fontweight="bold", color=cc["text"]
            )

        self.axes.set_facecolor("none")
        self.axes.set_xlabel("الحجم (MB)", fontsize=10, color=cc["axis_label"], labelpad=6)
        self.axes.tick_params(axis="y", labelsize=11, colors=cc["text"], length=0, pad=8)
        self.axes.tick_params(axis="x", labelsize=9, colors=cc["muted"])
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        self.axes.spines["bottom"].set_visible(True)
        self.axes.spines["bottom"].set_color(cc["spine"])

        self.fig.set_facecolor("none")
        self.draw()

    def refresh_theme(self):
        """يعيد الرسم بألوان الثيم الجديد"""
        if getattr(self, "_last", None):
            self.update_chart(*self._last)
        elif self.isVisibleTo(self.parentWidget()):
            self.setVisible(False)


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

        # خيارات الضغط
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)
        self.button_group = QButtonGroup(self)

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
        options_layout.addWidget(self.recommended_card)
        options_layout.addWidget(self.extreme_card)
        layout.addLayout(options_layout)

        # خيار استخدام Ghostscript (اختياري — لضغط أقوى)
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

        # زر التنفيذ
        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("ضغط الملف")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run_compress)
        run_layout.addStretch()
        run_layout.addWidget(self.run_btn)
        layout.addLayout(run_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # الرسم البياني
        self.chart = CompressChart(self)
        layout.addWidget(self.chart)

        layout.addStretch()

    def _on_file_selected(self, paths):
        if not paths:
            return
        path = paths[0]
        if not path.lower().endswith(".pdf"):
            QMessageBox.warning(self, "خطأ", "الرجاء اختيار ملف PDF فقط")
            return
        self.selected_file = path
        size = format_size(os.path.getsize(path))
        self.file_label.setText(f"📄 {os.path.basename(path)}  ({size})")
        self.run_btn.setEnabled(True)
        self.status_label.setText("")
        self.chart.setVisible(False)

    def _run_compress(self):
        if not self.selected_file:
            return

        level = self.recommended_card.value if self.recommended_card.radio.isChecked() else self.extreme_card.value
        use_gs = self.gs_check.isChecked()

        suggested_name = os.path.splitext(os.path.basename(self.selected_file))[0] + "_مضغوط.pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ الملف المضغوط", suggested_name, "PDF Files (*.pdf)"
        )
        if not output_path:
            return

        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("⏳  جاري الضغط... يرجى الانتظار")
        self.status_label.setObjectName("")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        self.chart.setVisible(False)

        self.worker = Worker(compress_pdf, self.selected_file, output_path,
                             level=level, use_ghostscript=use_gs)
        self.worker.finished_ok.connect(lambda res: self._on_success(res, output_path))
        self.worker.failed.connect(self._on_failure)
        self.worker.start()

    def _on_success(self, result, output_path):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)

        orig = format_size(result["original_size"])
        comp = format_size(result["compressed_size"])
        pct = result["reduction_percent"]
        method = result.get("method", "غير معروف")

        if pct > 0:
            pct_text = f"تم توفير {pct}% من الحجم 🎉"
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

    def _on_failure(self, error_msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setObjectName("statusError")
        self.status_label.setText(f"❌  فشلت العملية:\n{error_msg}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        self.chart.setVisible(False)
