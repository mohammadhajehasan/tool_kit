"""تبويب فك ضغط الأرشيفات — واجهة متسقة مع بقية أدوات النظام"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QCheckBox, QButtonGroup, QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices

from ui.widgets import DropZone, FileListWidget, make_toolbar_button
from ui.compress_tab import OptionCard
from core.archive_extract import (
    extract_many, is_supported_archive, archives_availability,
)


class ExtractWorker(QThread):
    """فك الضغط في خيط منفصل — يرسل تقدماً حياً ونتائج مفصلة"""

    progress_msg = Signal(str)
    progress_value = Signal(int)
    finished_ok = Signal(list)      # list[{archive, dest, files, skipped, error?}]
    failed = Signal(str)

    def __init__(self, paths, dest_dir, parent=None):
        super().__init__(parent)
        self.paths = paths
        self.dest_dir = dest_dir

    def run(self):
        try:
            results = extract_many(
                self.paths,
                dest_dir=self.dest_dir,
                progress=self._progress,
            )
            self.finished_ok.emit(results)
        except Exception as e:
            self.failed.emit(str(e))

    def _progress(self, message: str, percent=None):
        self.progress_msg.emit(message)
        if percent is not None:
            self.progress_value.emit(int(percent))


class ArchiveTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("فك ضغط الأرشيفات")
        title.setObjectName("pageTitle")
        desc = QLabel("استخرج محتوى الأرشيفات المضغوطة — يدعم ZIP و7z وRAR وTAR وGZIP وغيرها")
        desc.setObjectName("pageDesc")
        layout.addWidget(title)
        layout.addWidget(desc)

        self.drop_zone = DropZone(
            hint_text="اسحب الأرشيفات هنا أو انقر للاختيار",
            sub_text="يمكن اختيار عدة أرشيفات في المرة الواحدة",
            file_filter="Archives Files (*.zip *.cbz *.7z *.rar *.cbr *.tar *.gz *.tgz *.bz2 *.tbz2 *.xz *.zst)",
            multiple=True,
            min_height=130,
        )
        self.drop_zone.filesDropped.connect(self._on_files_added)
        layout.addWidget(self.drop_zone)

        self.file_list = FileListWidget()
        self.file_list.setMinimumHeight(100)
        self.file_list.filesChanged.connect(self._update_state)
        layout.addWidget(self.file_list)

        toolbar = QHBoxLayout()
        self.remove_btn = make_toolbar_button("حذف المحدد", danger=True)
        self.remove_btn.clicked.connect(self.file_list.remove_selected)
        self.clear_btn = make_toolbar_button("مسح الكل", danger=True)
        self.clear_btn.clicked.connect(self.file_list.clear_all)
        toolbar.addWidget(self.remove_btn)
        toolbar.addWidget(self.clear_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # خيارات الوجهة
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)
        self.dest_group = QButtonGroup(self)

        self.adjacent_card = OptionCard(
            "بجانب كل أرشيف",
            "ينشئ مجلداً باسم الأرشيف نفسه بجوار مكان الملف",
            "adjacent",
            self.dest_group,
            checked=True,
        )
        self.custom_card = OptionCard(
            "مجلد محدد",
            "يستخرج محتوى كل الأرشيفات إلى مجلد واحد تختاره",
            "custom",
            self.dest_group,
        )
        options_layout.addWidget(self.adjacent_card)
        options_layout.addWidget(self.custom_card)
        layout.addLayout(options_layout)

        # اختيار مجلد مخصص (يظهر بجانب خيار "مجلد محدد")
        folder_row = QHBoxLayout()
        folder_row.setSpacing(8)
        self.folder_path = None
        self.folder_label = QLabel("لم يُحدد مجلد بعد")
        self.folder_label.setObjectName("hintLabel")
        self.browse_btn = QPushButton("📁 اختيار المجلد…")
        self.browse_btn.setObjectName("secondaryBtn")
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.clicked.connect(self._choose_folder)
        folder_row.addWidget(self.browse_btn)
        folder_row.addWidget(self.folder_label, 1)
        layout.addLayout(folder_row)

        # فتح مجلد النتيجة بعد الانتهاء
        self.open_check = QCheckBox("فتح مجلد النتيجة تلقائياً بعد الانتهاء")
        self.open_check.setChecked(True)
        layout.addWidget(self.open_check)

        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("فك الضغط")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run_extract)
        run_layout.addStretch()
        run_layout.addWidget(self.run_btn)
        layout.addLayout(run_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch()

        self._hint_availability()

    # ---------- مساعدة ----------
    def _hint_availability(self):
        """تنبيه ودّي من سطر واحد عن الصيغ التي تحتاج مكتبات اختيارية"""
        available = archives_availability()
        tips = []
        if not available.get("rar"):
            tips.append("rarfile")
        if not available.get("7z"):
            tips.append("py7zr")
        if not available.get("zstd"):
            tips.append("zstandard")
        if tips:
            self.status_label.setObjectName("hintLabel")
            self.status_label.setText(
                "ℹ️ صيغ تعمل بعد تثبيت مكتباتها الاختيارية: pip install " + " / ".join(tips)
            )
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

    def _show_status(self, key: str, text: str):
        self.status_label.setObjectName(key)
        self.status_label.setText(text)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    # ---------- أحداث ----------
    def _on_files_added(self, paths):
        supported, skipped = [], 0
        for p in paths:
            if is_supported_archive(p):
                supported.append(p)
            else:
                skipped += 1

        if skipped:
            self._show_status("statusError",
                              f"⛔  تم تجاهل {skipped} ملف بصيغة غير مدعومة")
        self.file_list.add_files(supported)
        self._update_state()

    def _update_state(self):
        use_custom = self.custom_card.radio.isChecked()
        ready = bool(self.file_list.get_paths())
        if use_custom:
            ready = ready and self.folder_path is not None
        self.run_btn.setEnabled(ready)

    def _choose_folder(self):
        d = QFileDialog.getExistingDirectory(self, "اختر مجلد الإخراج")
        if d:
            self.folder_path = d
            self.folder_label.setText(f"📁  {d}")
            self._update_state()

    # ---------- التنفيذ ----------
    def _run_extract(self):
        paths = self.file_list.get_paths()
        if not paths:
            return
        dest_dir = None
        if self.custom_card.radio.isChecked():
            if not self.folder_path:
                QMessageBox.information(self, "تنبيه", "اختر مجلد الإخراج أولاً")
                return
            dest_dir = self.folder_path

        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self._show_status("", "⏳  جاري فك ضغط الأرشيفات…")

        self.worker = ExtractWorker(paths, dest_dir)
        self.worker.progress_msg.connect(self._on_progress_msg)
        self.worker.progress_value.connect(self.progress.setValue)
        self.worker.finished_ok.connect(self._on_success)
        self.worker.failed.connect(self._on_failure)
        self.worker.start()

    def _on_progress_msg(self, msg):
        self.status_label.setText(f"⏳  {msg}")

    def _on_success(self, results):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)

        ok = [r for r in results if r.get("dest")]
        failed = [r for r in results if not r.get("dest")]

        if not ok:
            self._on_failure(failed[0]["error"] if failed else "لا نتائج")
            return

        total_files = sum(r["files"] for r in ok)
        lines = [f"• {os.path.basename(r['archive'])}  →  {r['files']} ملف" for r in ok]
        text = (
            f"✅  تم فك ضغط {len(ok)} أرشيف بنجاح — إجمالي الملفات: {total_files}\n\n"
            + "\n".join(lines)
        )
        if failed:
            text += "\n\n⚠️  فشل تحليل ما يلي:\n" + "\n".join(
                f"• {os.path.basename(f['archive'])}: {f['error']}" for f in failed
            )
        self._show_status("statusSuccess", text)

        if self.open_check.isChecked():
            QDesktopServices.openUrl(QUrl.fromLocalFile(ok[0]["dest"]))

    def _on_failure(self, error_msg):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self._show_status("statusError", f"❌  فشلت العملية:\n{error_msg}")
