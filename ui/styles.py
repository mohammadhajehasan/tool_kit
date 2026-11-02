"""
تنسيقات QSS — تصميم عصري جذاب (Modern Flat)
"""

APP_STYLE = """
/* ═══════════════════════════════════════════
   عام — خطوط وألوان أساسية
   ═══════════════════════════════════════════ */
* {
    font-family: "Cairo", "Tajawal", "Segoe UI", "Tahoma", "Arial";
    font-size: 14px;
    color: #1e293b;
}

 QMainWindow,
 QWidget#centralWidget {
     background-color: #f1f5f9;
 }

/* ═══════════════════════════════════════════
   الشريط الجانبي — الخلفيات
   ═══════════════════════════════════════════ */
QWidget#sidebarContainer {
    background-color: #0f172a;
}

QWidget#sidebarHeader {
    background-color: #0f172a;
}

QWidget#sidebarFooter {
    background-color: #0f172a;
}

/* ═══════════════════════════════════════════
   الشريط الجانبي
   ═══════════════════════════════════════════ */
QListWidget#sidebar {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #0f172a, stop:1 #1e293b
    );
    border: none;
    padding: 16px 10px;
    outline: none;
}

QListWidget#sidebar::item {
    color: #94a3b8;
    padding: 15px 18px;
    border-radius: 12px;
    margin: 3px 6px;
    font-weight: 500;
    font-size: 14px;
}

QListWidget#sidebar::item:selected {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #8b5cf6
    );
    color: white;
    font-weight: 700;
    font-size: 14px;
}

QListWidget#sidebar::item:hover:!selected {
    background-color: rgba(255, 255, 255, 0.07);
    color: #cbd5e1;
}

QLabel#appTitle {
    color: white;
    font-size: 20px;
    font-weight: 800;
    padding: 28px 18px 6px 18px;
    letter-spacing: 0.5px;
    background-color: #0f172a;
}

QLabel#appSubtitle {
    color: #64748b;
    font-size: 12px;
    padding: 0px 18px 22px 18px;
    font-weight: 400;
    background-color: #0f172a;
}

/* ═══════════════════════════════════════════
   منطقة المحتوى — البطاقة الرئيسية
   ═══════════════════════════════════════════ */
QWidget#pageContainer {
    background-color: white;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
}

QLabel#pageTitle {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
}

QLabel#pageDesc {
    font-size: 13px;
    color: #64748b;
    font-weight: 400;
}

/* ═══════════════════════════════════════════
   منطقة السحب والإفلات
   ═══════════════════════════════════════════ */
QFrame#dropZone {
    background-color: #f8fafc;
    border: 2.5px dashed #cbd5e1;
    border-radius: 16px;
}

QFrame#dropZone:hover {
    border-color: #6366f1;
    background-color: #eef2ff;
}

QLabel#dropIcon {
    font-size: 42px;
}

QLabel#dropText {
    color: #334155;
    font-size: 15px;
    font-weight: 600;
}

QLabel#dropSubtext {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 400;
}

/* ═══════════════════════════════════════════
   قائمة الملفات
   ═══════════════════════════════════════════ */
QListWidget#fileList {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 6px;
}

QListWidget#fileList::item {
    padding: 12px 12px;
    border-bottom: 1px solid #f1f5f9;
    border-radius: 8px;
    margin: 2px 0;
}

QListWidget#fileList::item:selected {
    background-color: #eef2ff;
    color: #1e293b;
    font-weight: 600;
}

QListWidget#fileList::item:hover:!selected {
    background-color: #f8fafc;
}

/* ═══════════════════════════════════════════
   الأزرار
   ═══════════════════════════════════════════ */
QPushButton {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 11px 22px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #e2e8f0;
    border-color: #cbd5e1;
}

QPushButton:pressed {
    background-color: #cbd5e1;
}

/* الزر الرئيسي */
QPushButton#primaryBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #8b5cf6
    );
    color: white;
    border: none;
    padding: 13px 36px;
    font-size: 15px;
    font-weight: 700;
    border-radius: 12px;
}

QPushButton#primaryBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #4f46e5, stop:1 #7c3aed
    );
}

QPushButton#primaryBtn:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #4338ca, stop:1 #6d28d9
    );
}

QPushButton#primaryBtn:disabled {
    background-color: #c7d2fe;
    color: #a5b4fc;
}

/* زر تغيير الثيم (في أعلى الشريط الجانبي) */
QPushButton#themeBtn {
    background-color: rgba(255, 255, 255, 0.10);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 700;
    margin: 8px 12px 4px 12px;
}

QPushButton#themeBtn:hover {
    background-color: rgba(255, 255, 255, 0.18);
    color: white;
    border-color: rgba(255, 255, 255, 0.30);
}

QPushButton#themeBtn:pressed {
    background-color: rgba(255, 255, 255, 0.25);
}

/* زرار الشريط الجانبي (تبديل النوع / الثيم) */
QPushButton#sidebarBtn {
    background-color: rgba(255, 255, 255, 0.07);
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#sidebarBtn:hover {
    background-color: rgba(255, 255, 255, 0.14);
    color: white;
    border-color: rgba(255, 255, 255, 0.25);
}

/* زر الخطر */
QPushButton#dangerBtn {
    background-color: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
}

QPushButton#dangerBtn:hover {
    background-color: #fee2e2;
    border-color: #fca5a5;
}

QPushButton#dangerBtn:pressed {
    background-color: #fca5a5;
    color: #991b1b;
}

/* ═══════════════════════════════════════════
   بطاقات الخيارات (Radio Cards)
   ═══════════════════════════════════════════ */
QRadioButton {
    padding: 6px;
    spacing: 10px;
    font-size: 14px;
}

QFrame#optionCard {
    background-color: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 14px;
}

QFrame#optionCard:hover {
    border-color: #c7d2fe;
    background-color: #f5f3ff;
}

QFrame#optionCard[selected="true"] {
    border: 2.5px solid #6366f1;
    background-color: #eef2ff;
}

QLabel#optionTitle {
    font-weight: 700;
    font-size: 14px;
    color: #0f172a;
}

QLabel#optionDesc {
    color: #64748b;
    font-size: 12px;
    font-weight: 400;
}

/* ═══════════════════════════════════════════
   شريط التقدم
   ═══════════════════════════════════════════ */
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #e2e8f0;
    max-height: 10px;
    min-height: 10px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #a78bfa
    );
    border-radius: 6px;
}

/* ═══════════════════════════════════════════
   رسائل الحالة
   ═══════════════════════════════════════════ */
QLabel#statusSuccess {
    color: #16a34a;
    font-weight: 700;
    font-size: 13px;
    padding: 10px;
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
}

QLabel#statusError {
    color: #dc2626;
    font-weight: 700;
    font-size: 13px;
    padding: 10px;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
}

/* ═══════════════════════════════════════════
   حقول الإدخال
   ═══════════════════════════════════════════ */
QLineEdit, QSpinBox {
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 14px;
    background-color: white;
    font-size: 14px;
    selection-background-color: #c7d2fe;
    selection-color: #1e293b;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #6366f1;
    background-color: #fafafe;
}

QLineEdit:hover, QSpinBox:hover {
    border-color: #cbd5e1;
}

QLineEdit::placeholder {
    color: #94a3b8;
    font-style: italic;
}

/* ═══════════════════════════════════════════
   حوار رسالة
   ═══════════════════════════════════════════ */
QMessageBox {
    background-color: white;
}

QMessageBox QLabel {
    color: #1e293b;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ═══════════════════════════════════════════
   شريط التمرير
   ═══════════════════════════════════════════ */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background-color: transparent;
}

/* ═══════════════════════════════════════════
   Tooltip
   ═══════════════════════════════════════════ */
QToolTip {
    background-color: #1e293b;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
}
"""

# ═══════════════════════════════════════════
#   لوحات الألوان حسب الجنس (للحوار والواجهة)
# ═══════════════════════════════════════════

MALE_PALETTE = {
    "primary": "#6366f1",
    "primary_dark": "#4f46e5",
    "accent": "#8b5cf6",
    "bg": "#eef2ff",
    "card": "#f5f3ff",
    "text": "#312e81",
    "muted": "#64748b",
    "selected_bg": "#e0e7ff",
    "border": "#c7d2fe",
}

FEMALE_PALETTE = {
    "primary": "#ec4899",
    "primary_dark": "#db2777",
    "accent": "#f472b6",
    "bg": "#fdf2f8",
    "card": "#fce7f3",
    "text": "#831843",
    "muted": "#94a3b8",
    "selected_bg": "#fbcfe8",
    "border": "#f9a8d4",
}

# أسماء لوحات — للاستخدام في القوائم
GENDER_PALETTES = {
    "male": MALE_PALETTE,
    "female": FEMALE_PALETTE,
}


# خرائط الألوان الافتراضية (الذكر = البنفسجي) إلى نظيرها الأنثوي (الوردي)
# تُستخدم لإعادة تلوين كامل APP_STYLE حسب الجنس المختار.
FEMALE_COLOR_MAP = {
    "#6366f1": "#ec4899",   # primary
    "#8b5cf6": "#f472b6",   # accent
    "#4f46e5": "#db2777",   # primary_dark
    "#7c3aed": "#ec4899",   # hover accent
    "#4338ca": "#db2777",   # pressed
    "#6d28d9": "#be185d",   # pressed accent
    "#c7d2fe": "#f9a8d4",   # border / disabled
    "#eef2ff": "#fdf2f8",   # bg-light
    "#f5f3ff": "#fce7f3",   # card bg
    "#e0e7ff": "#fbcfe8",   # selected bg
    "#a78bfa": "#f9a8d4",   # progress chunk
}


def get_style(gender: str = "male") -> str:
    """
    يرجع سلسلة QSS كاملة (نفس هيكل APP_STYLE) مخصصة للجنس المحدد.

    gender: "male" -> يبقي البنفسجي (APP_STYLE الأصلية)
    gender: "female" -> يستبدل كل ألوان البنفسجي/النيلي بنظيرها الوردي
    """
    # تطبيع قيمة الجنس إلى أحرف صغيرة لتفادي مشاكل حالة الأحرف (Male/Female...)
    gender = str(gender).lower()

    style = APP_STYLE
    if gender == "female":
        for old, new in FEMALE_COLOR_MAP.items():
            style = style.replace(old, new)
    return style
