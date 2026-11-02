import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QMessageBox, QRadioButton, QButtonGroup, QProgressBar,
    QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage

from ui.widgets import DropZone, Worker
from core.split import (
    get_page_count, parse_page_ranges, extract_pages,
    split_to_individual_files, render_page_thumbnails, SplitError
)


class ClickablePageCard(QFrame):
    """بطاقة صفحة قابلة للنقر — تسمح باختيار/إلغاء اختيار الصفحة"""

    clicked = Signal(int)  # يرسل فهرس الصفحة (من 0)

    def __init__(self, page_index: int, parent=None):
        super().__init__(parent)
        self.page_index = page_index
        self.is_selected = False
        self.setFixedSize(100, 130)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QFrame { background-color: white; border: 2px solid #e2e8f0; border-radius: 8px; }"
        )

        self.v = QVBoxLayout(self)
        self.v.setContentsMargins(4, 4, 4, 4)
        self.v.setSpacing(2)

        # منطقة الصورة
        self.image_label = QLabel("⏳")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(90)
        self.v.addWidget(self.image_label)

        # رقم الصفحة
        self.num_label = QLabel(f"صفحة {page_index + 1}")
        self.num_label.setAlignment(Qt.AlignCenter)
        self.num_label.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        self.v.addWidget(self.num_label)

    def set_image(self, pixmap: QPixmap):
        """يعرض صورة مصغّرة للصفحة"""
        if pixmap is not None:
            scaled = pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("⚠️")

    def set_selected(self, selected: bool):
        """يحدد حالة الاختيار ويحدّث التنسيق"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet(
                "QFrame { background-color: #eef2ff; border: 3px solid #6366f1; border-radius: 8px; }"
            )
            self.num_label.setStyleSheet("font-size: 10px; color: #4f46e5; font-weight: 800;")
        else:
            self.setStyleSheet(
                "QFrame { background-color: white; border: 2px solid #e2e8f0; border-radius: 8px; }"
            )
            self.num_label.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.page_index)
        super().mousePressEvent(event)


class PageGrid(QScrollArea):
    """
    شبكة صفحات قابلة للتمرير عمودياً.
    تسمح بالنقر على الصفحات لاختيارها/إلغاء اختيارها.
    """

    selectionChanged = Signal(set)  # يرسل مجموعة الفهارس المحددة

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMinimumHeight(150)
        self.setMaximumHeight(300)
        self.setStyleSheet(
            "QScrollArea { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; }"
        )

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setSpacing(8)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setWidget(self.container)

        self.cards: list[ClickablePageCard] = []
        self.selected_pages: set[int] = set()

    def clear_pages(self):
        """يزيل كل البطاقات"""
        while self.grid.count() > 0:
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cards = []
        self.selected_pages = set()

    def set_pages(self, images, selected_indices=None):
        """
        يعرض الصفحات في شبكة.
        images: قائمة PIL.Image أو None.
        selected_indices: مجموعة فهارس الصفحات المحددة (فهرسة من 0).
        """
        self.clear_pages()
        self.selected_pages = set(selected_indices) if selected_indices else set()

        cols = 5  # عدد الأعمدة في الشبكة

        for idx, img in enumerate(images):
            card = ClickablePageCard(idx)
            card.clicked.connect(self._on_card_clicked)

            # تحويل PIL.Image إلى QPixmap
            if img is not None:
                try:
                    if img.mode == "RGBA":
                        qimg = QImage(img.tobytes(), img.width, img.height, img.width * 4, QImage.Format_RGBA8888)
                    else:
                        rgb = img.convert("RGB")
                        qimg = QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3, QImage.Format_RGB888)
                    pm = QPixmap.fromImage(qimg)
                    card.set_image(pm)
                except Exception:
                    card.set_image(None)
            else:
                card.set_image(None)

            # تطبيق حالة الاختيار
            card.set_selected(idx in self.selected_pages)

            row = idx // cols
            col = idx % cols
            self.grid.addWidget(card, row, col)
            self.cards.append(card)

    def _on_card_clicked(self, page_index: int):
        """يعالج النقر على بطاقة صفحة"""
        if page_index in self.selected_pages:
            self.selected_pages.discard(page_index)
        else:
            self.selected_pages.add(page_index)

        # تحديث حالة البطاقة
        self.cards[page_index].set_selected(page_index in self.selected_pages)

        # إرسال إشارة التغيير
        self.selectionChanged.emit(set(self.selected_pages))

    def set_selected(self, selected_indices):
        """يحدد الصفحات المحددة برمجياً (من حقل النطاق)"""
        self.selected_pages = set(selected_indices)
        for card in self.cards:
            card.set_selected(card.page_index in self.selected_pages)


class SplitTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.total_pages = 0
        self.worker = None
        self.all_images = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("تقطيع ملف PDF")
        title.setObjectName("pageTitle")
        desc = QLabel("استخرج صفحات محددة من ملف PDF — انقر على الصفحات لاختيارها أو أدخل النطاق يدوياً")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            sub_text="ملف واحد",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file_selected)
        layout.addWidget(self.drop_zone)

        self.file_label = QLabel("")
        self.file_label.setStyleSheet("color: #334155; font-weight: 600; font-size: 14px; padding: 4px 0;")
        layout.addWidget(self.file_label)

        # شبكة المعاينات المصغّرة (قابلة للتمرير والنقر)
        self.preview_title = QLabel("معاينة الصفحات — انقر على الصفحات لاختيارها:")
        self.preview_title.setStyleSheet("color: #334155; font-weight: 700; font-size: 13px;")
        self.preview_title.setVisible(False)
        layout.addWidget(self.preview_title)

        self.page_grid = PageGrid()
        self.page_grid.setVisible(False)
        self.page_grid.selectionChanged.connect(self._on_pages_selected)
        layout.addWidget(self.page_grid)

        # إدخال نطاق الصفحات
        range_layout = QHBoxLayout()
        range_layout.setSpacing(12)
        range_label = QLabel("الصفحات المطلوبة:")
        range_label.setStyleSheet("font-weight: 600; color: #334155;")
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("مثال: 1-3,5,8-10")
        self.range_input.setEnabled(False)
        self.range_input.textChanged.connect(self._on_range_changed)
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.range_input, 1)
        layout.addLayout(range_layout)

        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 400;")
        layout.addWidget(self.hint_label)

        self.selected_title = QLabel("")
        self.selected_title.setStyleSheet("color: #6366f1; font-size: 12px; font-weight: 700;")
        layout.addWidget(self.selected_title)

        # وضع الإخراج
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(16)
        self.mode_group = QButtonGroup(self)
        self.single_radio = QRadioButton("دمج الصفحات المحددة في ملف واحد")
        self.single_radio.setChecked(True)
        self.individual_radio = QRadioButton("كل صفحة كملف مستقل")
        self.mode_group.addButton(self.single_radio)
        self.mode_group.addButton(self.individual_radio)
        mode_layout.addWidget(self.single_radio)
        mode_layout.addWidget(self.individual_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("تقطيع الملف")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run_split)
        run_layout.addStretch()
        run_layout.addWidget(self.run_btn)
        layout.addLayout(run_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 8px;")
        layout.addWidget(self.status_label)

    def _on_file_selected(self, paths):
        if not paths:
            return
        path = paths[0]
        if not path.lower().endswith(".pdf"):
            QMessageBox.warning(self, "خطأ", "الرجاء اختيار ملف PDF فقط")
            return
        try:
            self.total_pages = get_page_count(path)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذّر قراءة الملف: {e}")
            return

        self.selected_file = path
        self.file_label.setText(f"📄 {os.path.basename(path)}")
        self.hint_label.setText(f"عدد صفحات الملف: {self.total_pages}")
        self.selected_title.setText("")
        self.range_input.setEnabled(True)
        self.run_btn.setEnabled(True)
        self.status_label.setText("")

        # إنشاء المعاينات في خيط منفصل حتى لا تتجمد الواجهة
        self.page_grid.setVisible(True)
        self.preview_title.setVisible(True)
        self.page_grid.set_pages([None] * self.total_pages)  # placeholder
        self.worker = Worker(render_page_thumbnails, path, 120)
        self.worker.finished_ok.connect(lambda imgs: self._on_thumbnails_ready(imgs))
        self.worker.failed.connect(lambda e: self._on_thumbnails_fail(e))
        self.worker.start()

    def _on_thumbnails_ready(self, images):
        self.all_images = images
        try:
            selected = parse_page_ranges(self.range_input.text(), self.total_pages)
        except SplitError:
            selected = set()
        self.page_grid.set_pages(images, selected_indices=selected)

    def _on_thumbnails_fail(self, error_msg):
        self.all_images = []
        self.page_grid.setVisible(False)
        self.preview_title.setVisible(False)

    def _on_pages_selected(self, selected_pages: set):
        """يُستدعى عند النقر على الصفحات — يحدّث حقل النطاق"""
        if not selected_pages:
            self.range_input.setText("")
            self.selected_title.setText("لم يتم تحديد أي صفحات")
            self.selected_title.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: 700;")
            return

        # تحويل المجموعة إلى نص نطاقات
        sorted_pages = sorted(selected_pages)
        ranges = []
        start = prev = sorted_pages[0]
        for p in sorted_pages[1:]:
            if p == prev + 1:
                prev = p
            else:
                if start == prev:
                    ranges.append(str(start + 1))
                else:
                    ranges.append(f"{start + 1}-{prev + 1}")
                start = prev = p
        if start == prev:
            ranges.append(str(start + 1))
        else:
            ranges.append(f"{start + 1}-{prev + 1}")

        range_text = ",".join(ranges)

        # منع إعادة الدخول (حتى لا يتكرر التحديث)
        self.range_input.blockSignals(True)
        self.range_input.setText(range_text)
        self.range_input.blockSignals(False)

        self.selected_title.setText(f"تم تحديد {len(selected_pages)} صفحة")
        self.selected_title.setStyleSheet("color: #16a34a; font-size: 12px; font-weight: 700;")

    def _on_range_changed(self, text):
        if not self.selected_file:
            return
        try:
            pages = parse_page_ranges(text, self.total_pages)
            self.selected_title.setText(f"سيتم تحديد {len(pages)} صفحة")
            self.selected_title.setStyleSheet("color: #16a34a; font-size: 12px; font-weight: 700;")
            if self.all_images:
                self.page_grid.set_selected(pages)
        except SplitError as e:
            self.selected_title.setText(str(e))
            self.selected_title.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: 700;")
            if self.all_images:
                self.page_grid.set_selected(set())

    def _run_split(self):
        if not self.selected_file:
            return

        try:
            pages = parse_page_ranges(self.range_input.text(), self.total_pages)
        except SplitError as e:
            QMessageBox.warning(self, "خطأ في تحديد الصفحات", str(e))
            return

        base_name = os.path.splitext(os.path.basename(self.selected_file))[0]

        if self.single_radio.isChecked():
            suggested_name = f"{base_name}_مقتطف.pdf"
            output_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ الملف الناتج", suggested_name, "PDF Files (*.pdf)"
            )
            if not output_path:
                return
            self._start_worker(extract_pages, self.selected_file, pages, output_path,
                                success_msg=lambda r: f"✅ تم استخراج {len(pages)} صفحة بنجاح\nحُفظ في: {output_path}")
        else:
            output_dir = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ")
            if not output_dir:
                return
            self._start_worker(split_to_individual_files, self.selected_file, output_dir, pages,
                                success_msg=lambda r: f"✅ تم إنشاء {len(r)} ملف مستقل\nحُفظت في: {output_dir}")

    def _start_worker(self, fn, *args, success_msg):
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("جاري التقطيع...")

        self.worker = Worker(fn, *args)
        self.worker.finished_ok.connect(lambda res: self._on_success(success_msg(res)))
        self.worker.failed.connect(self._on_failure)
        self.worker.start()

    def _on_success(self, message):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setObjectName("statusSuccess")
        self.status_label.setText(message)
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)

    def _on_failure(self, error_msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setObjectName("statusError")
        self.status_label.setText(f"❌ فشلت العملية: {error_msg}")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)