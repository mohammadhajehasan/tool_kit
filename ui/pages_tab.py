"""تبويب محرر الصفحات — إعادة ترتيب بالسحب، تدوير، حذف، ثم حفظ."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QProgressBar, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QTransform

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from ui.i18n import tr
from core.pages import organize, rotate_value, PagesError
from core.split import render_page_thumbnails
from core.history import record

PDF_FILTER = "PDF (*.pdf)"


class PagesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.src_path = None
        self.total_pages = 0
        self.rotations: dict[int, int] = {}  # فهرس أصلي → زاوية
        self._pixmaps: dict[int, QPixmap] = {}  # فهرس أصلي → صورة مصغرة
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(tr("pages_title"))
        title.setObjectName("pageTitle")
        desc = QLabel(tr("pages_desc"))
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            sub_text="ثم اسحب الصفحات لإعادة ترتيبها",
            file_filter=PDF_FILTER, multiple=False,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.rotate_btn = QPushButton("↻  تدوير المحدد")
        self.rotate_btn.setObjectName("secondaryBtn")
        self.rotate_btn.clicked.connect(self._rotate_selected)
        self.delete_btn = QPushButton("🗑  حذف المحدد")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_selected)
        self.reset_btn = QPushButton("↩  استرجاع الأصل")
        self.reset_btn.setObjectName("secondaryBtn")
        self.reset_btn.clicked.connect(self._reset)
        self.count_label = QLabel("")
        self.count_label.setObjectName("hintLabel")
        for w in (self.rotate_btn, self.delete_btn, self.reset_btn, self.count_label):
            toolbar.addWidget(w)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.grid = QListWidget()
        self.grid.setObjectName("pagesGrid")
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setFlow(QListWidget.LeftToRight)
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setDragDropMode(QListWidget.InternalMove)
        self.grid.setDefaultDropAction(Qt.MoveAction)
        self.grid.setSelectionMode(QListWidget.ExtendedSelection)
        self.grid.setIconSize(QSize(96, 120))
        self.grid.setUniformItemSizes(True)
        self.grid.setMinimumHeight(320)
        layout.addWidget(self.grid, 1)

        save_row = QHBoxLayout()
        self.save_btn = QPushButton(tr("save_result"))
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save)
        save_row.addStretch()
        save_row.addWidget(self.save_btn)
        layout.addLayout(save_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    # ---------- تحميل ----------
    def _on_file(self, paths):
        if not paths or self.worker:
            return
        self.src_path = paths[0]
        self.drop_zone.setVisible(False)
        self.progress.setVisible(True)
        self.status_label.setText("⏳ جارٍ توليد المعاينات…")
        self.worker = Worker(self._load_thumbs)
        self.worker.finished_ok.connect(self._on_loaded)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _load_thumbs(self):
        return render_page_thumbnails(self.src_path, max_width=190)

    def _on_loaded(self, images):
        self.worker = None
        self.progress.setVisible(False)
        self.rotations = {}
        self._pixmaps = {}
        self.grid.clear()
        self.total_pages = len(images)
        for idx, img in enumerate(images):
            pix = self._to_pixmap(img)
            self._pixmaps[idx] = pix
            self._add_item(idx)
        self._update_count()
        self.save_btn.setEnabled(True)
        self.status_label.setText(f"✅ {self.total_pages} صفحة — اسحب لإعادة الترتيب، حدد صفحة للتدوير/الحذف")

    def _to_pixmap(self, img) -> QPixmap:
        if img is None:
            return QPixmap()
        from PIL import Image
        data = img.convert("RGB").tobytes()
        qimg = QPixmap.fromImage(
            QImage_helper(data, img.width, img.height)
        )
        return qimg

    def _add_item(self, idx: int):
        deg = self.rotations.get(idx, 0)
        pix = self._pixmaps.get(idx)
        if pix and pix.isNull() is False:
            shown = pix.transformed(QTransform().rotate(deg), Qt.SmoothTransformation)
            icon = QIcon(shown)
        else:
            icon = QIcon()
        item = QListWidgetItem(icon, f"صفحة {idx + 1}")
        item.setData(Qt.UserRole, idx)
        item.setSizeHint(QSize(116, 152))
        item.setToolTip(f"الصفحة الأصلية رقم {idx + 1}" + (f" (مدورة {deg}°)" if deg else ""))
        self.grid.addItem(item)

    # ---------- عمليات ----------
    def _selected_indices(self) -> list[int]:
        return [it.data(Qt.UserRole) for it in self.grid.selectedItems()]

    def _rotate_selected(self):
        items = self.grid.selectedItems()
        if not items:
            show_toast(self, "حدد صفحة أو أكثر أولاً", "warning")
            return
        for item in items:
            idx = item.data(Qt.UserRole)
            self.rotations[idx] = rotate_value(self.rotations.get(idx, 0))
            deg = self.rotations[idx]
            pix = self._pixmaps.get(idx)
            if pix:
                shown = pix.transformed(QTransform().rotate(deg), Qt.SmoothTransformation)
                item.setIcon(QIcon(shown))
            item.setToolTip(f"الصفحة الأصلية رقم {idx + 1} (مدورة {deg}°)")

    def _delete_selected(self):
        items = self.grid.selectedItems()
        if not items:
            show_toast(self, "حدد الصفحات التي تريد حذفها", "warning")
            return
        remaining = self.grid.count() - len(items)
        if remaining == 0:
            show_toast(self, "لا يمكن حذف كل الصفحات — احذف بعضها فقط", "warning")
            return
        for item in items:
            self.grid.takeItem(self.grid.row(item))
        self._update_count()

    def _reset(self):
        self.rotations = {}
        self.grid.clear()
        for idx in range(self.total_pages):
            self._add_item(idx)
        self._update_count()

    def _update_count(self):
        self.count_label.setText(f"📄 {self.grid.count()} من {self.total_pages} صفحة")

    def _save(self):
        order = []
        for i in range(self.grid.count()):
            order.append(self.grid.item(i).data(Qt.UserRole))
        if not order:
            show_toast(self, "لا توجد صفحات للحفظ", "warning")
            return

        default = os.path.splitext(self.src_path)[0] + "_معدل.pdf"
        out, _ = QFileDialog.getSaveFileName(
            self, "حفظ الملف الجديد", default, "PDF (*.pdf)")
        if not out:
            return
        self.save_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("⏳ جارٍ الحفظ…")
        self.worker = Worker(organize, self.src_path, out, order, dict(self.rotations))
        result_holder = {"out": out}
        self.worker.finished_ok.connect(lambda _: self._on_saved(result_holder["out"]))
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _on_saved(self, out):
        self.worker = None
        self.progress.setVisible(False)
        self.save_btn.setEnabled(True)
        show_toast(self, "✅ تم حفظ الملف بنجاح", "info")
        self.status_label.setText(f"✅ محفوظ: {out}")
        record("محرر الصفحات", out)

    def _on_fail(self, err):
        self.worker = None
        self.progress.setVisible(False)
        self.save_btn.setEnabled(True)
        self.status_label.setText(f"❌ {err}")


def QImage_helper(data, width, height):
    """مُساعد تحويل bytes من PIL إلى QImage دون نسخ زائد."""
    from PySide6.QtGui import QImage
    img = QImage(data, width, height, 3 * width, QImage.Format_RGB888)
    return img.copy()
