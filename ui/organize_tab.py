"""تبويب تنظيم الصفحات: تدوير، حذف، وإعادة ترتيب بالسحب."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QListWidget, QListWidgetItem, QAbstractItemView,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage, QIcon

from ui.widgets import DropZone, Worker
from ui.toast import show_toast
from core.split import render_page_thumbnails, get_page_count
from core.organize import apply_organize, OrganizeError


class OrganizeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.total_pages = 0
        self.worker = None
        # كل عنصر: {'orig': int, 'rot': int, 'deleted': bool}
        self.pages_meta: list[dict] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("تنظيم الصفحات")
        title.setObjectName("pageTitle")
        desc = QLabel("أعد ترتيب الصفحات بالسحب، دوّرها أو احذفها ثم احفظ المستند")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب ملف PDF هنا أو انقر للاختيار",
            sub_text="ملف واحد",
            file_filter="PDF Files (*.pdf)",
            multiple=False,
            min_height=130,
        )
        self.drop_zone.filesDropped.connect(self._on_file)
        layout.addWidget(self.drop_zone)

        self.file_label = QLabel("")
        self.file_label.setObjectName("fileMeta")
        layout.addWidget(self.file_label)

        self.list = QListWidget()
        self.list.setObjectName("fileList")
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setIconSize(QSize(90, 110))
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setMovement(QListWidget.Snap)
        self.list.setDragDropMode(QAbstractItemView.InternalMove)
        self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.setMinimumHeight(220)
        self.list.setSpacing(8)
        layout.addWidget(self.list)

        tools = QHBoxLayout()
        self.rot_left = QPushButton("↺ 90°")
        self.rot_left.clicked.connect(lambda: self._rotate(-90))
        self.rot_right = QPushButton("↻ 90°")
        self.rot_right.clicked.connect(lambda: self._rotate(90))
        self.rot_180 = QPushButton("180°")
        self.rot_180.clicked.connect(lambda: self._rotate(180))
        self.del_btn = QPushButton("حذف المحدد")
        self.del_btn.setObjectName("dangerBtn")
        self.del_btn.clicked.connect(self._delete_selected)
        tools.addWidget(self.rot_left)
        tools.addWidget(self.rot_right)
        tools.addWidget(self.rot_180)
        tools.addWidget(self.del_btn)
        tools.addStretch()
        layout.addLayout(tools)

        run_row = QHBoxLayout()
        self.run_btn = QPushButton("حفظ المستند المنظّم")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        run_row.addStretch()
        run_row.addWidget(self.run_btn)
        layout.addLayout(run_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    def _on_file(self, paths):
        if not paths or not paths[0].lower().endswith(".pdf"):
            show_toast(self, "الرجاء اختيار ملف PDF", "warning")
            return
        path = paths[0]
        try:
            self.total_pages = get_page_count(path)
        except Exception as e:
            show_toast(self, f"تعذّر قراءة الملف: {e}", "error")
            return
        self.selected_file = path
        self.file_label.setText(f"📄 {os.path.basename(path)} — {self.total_pages} صفحة")
        self.list.clear()
        self.pages_meta = [{"orig": i, "rot": 0, "deleted": False} for i in range(self.total_pages)]
        self.run_btn.setEnabled(True)
        self.status_label.setText("جاري تحميل المعاينات...")
        self.worker = Worker(render_page_thumbnails, path, 100)
        self.worker.finished_ok.connect(self._thumbs_ready)
        self.worker.failed.connect(lambda e: show_toast(self, e, "error"))
        self.worker.start()

    def _pil_to_icon(self, img) -> QIcon:
        if img is None:
            return QIcon()
        try:
            rgb = img.convert("RGB")
            qimg = QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3, QImage.Format_RGB888)
            return QIcon(QPixmap.fromImage(qimg))
        except Exception:
            return QIcon()

    def _thumbs_ready(self, images):
        self.list.clear()
        for i, img in enumerate(images):
            item = QListWidgetItem(f"صفحة {i + 1}")
            item.setIcon(self._pil_to_icon(img))
            item.setData(Qt.UserRole, i)  # فهرس أصلي
            item.setData(Qt.UserRole + 1, 0)  # دوران تراكمي
            item.setSizeHint(QSize(110, 140))
            self.list.addItem(item)
        self.status_label.setText("اسحب لإعادة الترتيب — حدد صفحات للتدوير أو الحذف")

    def _rotate(self, deg: int):
        for item in self.list.selectedItems():
            cur = item.data(Qt.UserRole + 1) or 0
            item.setData(Qt.UserRole + 1, (cur + deg) % 360)
            orig = (item.data(Qt.UserRole) or 0) + 1
            rot = item.data(Qt.UserRole + 1)
            item.setText(f"صفحة {orig}" + (f"\n↺{rot}°" if rot else ""))
        show_toast(self, f"تم تدوير المحدد بمقدار {deg}°", "info", 1800)

    def _delete_selected(self):
        for item in list(self.list.selectedItems()):
            self.list.takeItem(self.list.row(item))
        if self.list.count() == 0:
            show_toast(self, "لا يمكن حذف كل الصفحات", "warning")
            # لا نستعيد هنا — المستخدم يعيد تحميل الملف
            self.run_btn.setEnabled(False)

    def _run(self):
        if not self.selected_file or self.list.count() == 0:
            return
        base = os.path.splitext(os.path.basename(self.selected_file))[0]
        output, _ = QFileDialog.getSaveFileName(
            self, "حفظ المستند", f"{base}_منظّم.pdf", "PDF Files (*.pdf)"
        )
        if not output:
            return

        # بناء ترتيب وعمليات من القائمة الحالية
        kept_orig = []
        rotations = {}
        for i in range(self.list.count()):
            item = self.list.item(i)
            orig = item.data(Qt.UserRole)
            rot = item.data(Qt.UserRole + 1) or 0
            kept_orig.append(orig)
            if rot:
                rotations[orig] = rot

        all_orig = set(range(self.total_pages))
        deleted = sorted(all_orig - set(kept_orig))

        # بعد الحذف تصبح الفهارس متتابعة حسب ترتيب kept_orig
        # apply_organize: rotate on original → delete → reorder remaining
        # new_order يجب أن يكون فهارس الوثيقة بعد الحذف
        # الصفحات المتبقية بعد الحذف بترتيب الفهرس الأصلي المتصاعد = [0..n-1] mapped
        remaining_sorted = sorted(kept_orig)
        index_map = {orig: new_i for new_i, orig in enumerate(remaining_sorted)}
        new_order = [index_map[o] for o in kept_orig]

        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("جاري الحفظ...")

        self.worker = Worker(
            apply_organize,
            self.selected_file,
            output,
            new_order=new_order,
            delete_indices=deleted,
            rotations=rotations or None,
        )
        self.worker.finished_ok.connect(lambda _: self._done(True, output))
        self.worker.failed.connect(lambda e: self._done(False, e))
        self.worker.start()

    def _done(self, ok, payload):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        if ok:
            self.status_label.setObjectName("statusSuccess")
            self.status_label.setText(f"✅ تم حفظ المستند المنظّم\n{payload}")
            show_toast(self, "تم حفظ المستند المنظّم", "success")
        else:
            self.status_label.setObjectName("statusError")
            self.status_label.setText(f"❌ {payload}")
            show_toast(self, str(payload), "error")
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
