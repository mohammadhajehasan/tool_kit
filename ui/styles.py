# نظام التصميم الحديث (Modern Design System) — PDF Toolbox
# 设计系统： gradients, glow, depth — نسخة مطورة بالكامل

# ---------- اللوحات اللونية ----------

LIGHT_COLORS = {
    # الأساسيات
    'primary': '#6366F1', 'primary_hover': '#4F46E5', 'primary_pressed': '#4338CA',
    'primary_light': '#EEF2FF', 'primary_dark': '#3730A3',
    'grad_from': '#6366F1', 'grad_to': '#8B5CF6',
    'grad_hover_from': '#4F46E5', 'grad_hover_to': '#7C3AED',
    'grad_pressed_from': '#4338CA', 'grad_pressed_to': '#6D28D9',
    'secondary': '#0EA5E9', 'secondary_hover': '#0284C7', 'secondary_light': '#E0F2FE',
    'accent': '#10B981', 'accent_hover': '#059669', 'accent_light': '#D1FAE5',
    'error': '#EF4444', 'error_hover': '#DC2626', 'error_light': '#FEE2E2',
    'warning': '#F59E0B', 'warning_light': '#FEF3C7',
    'success_text': '#166534', 'success_bg': '#F0FDF4', 'success_border': '#BBF7D0',
    'error_text': '#B91C1C', 'error_bg': '#FEF2F2', 'error_border': '#FECACA',
    # الخلفيات
    'bg_main': '#F1F4FA',
    'bg_surface': '#FFFFFF',
    'bg_card_hover': '#F8FAFF',
    'bg_sidebar': '#0B1024', 'bg_sidebar_1': '#131A3E', 'bg_sidebar_2': '#0B1024',
    'bg_sidebar_item': '#1E293B', 'bg_sidebar_selected_from': '#6366F1', 'bg_sidebar_selected_to': '#8B5CF6',
    'bg_hover_soft': 'rgba(99, 102, 241, 0.08)',
    'bg_active_soft': 'rgba(99, 102, 241, 0.14)',
    # النصوص
    'text_primary': '#0F172A', 'text_secondary': '#3B4A63', 'text_muted': '#8B96AC',
    'text_inverse': '#FFFFFF', 'text_sidebar': '#A3AEC8', 'text_sidebar_hover': '#FFFFFF',
    'text_sidebar_selected': '#FFFFFF', 'text_on_primary': '#FFFFFF',
    # الحدود والمدخلات
    'border': '#E3E8F2', 'border_light': '#EEF1F8', 'border_focus': '#6366F1',
    'border_error': '#FCA5A5',
    'input_bg': '#FFFFFF', 'input_border': '#C7D0E0', 'input_focus_border': '#6366F1',
    'input_placeholder': '#94A3B8',
    'sidebar_border': 'rgba(255, 255, 255, 0.07)',
    'sidebar_separator': 'rgba(255, 255, 255, 0.06)',
}

DARK_COLORS = {
    # الأساسيات
    'primary': '#8B93FF', 'primary_hover': '#A5B4FC', 'primary_pressed': '#6C74F5',
    'primary_light': '#23224E', 'primary_dark': '#312E81',
    'grad_from': '#6D6FFA', 'grad_to': '#A855F7',
    'grad_hover_from': '#8789FF', 'grad_hover_to': '#BD7DF9',
    'grad_pressed_from': '#585BE8', 'grad_pressed_to': '#9343EE',
    'secondary': '#22D3EE', 'secondary_hover': '#67E8F9', 'secondary_light': '#164E63',
    'accent': '#34D399', 'accent_hover': '#6EE7B7', 'accent_light': '#065F46',
    'error': '#F87171', 'error_hover': '#FB7185', 'error_light': '#7F1D1D',
    'warning': '#FBBF24', 'warning_light': '#451A03',
    'success_text': '#86EFAC', 'success_bg': '#102A1C', 'success_border': '#14532D',
    'error_text': '#FCA5A5', 'error_bg': '#2A1214', 'error_border': '#7F1D1D',
    # الخلفيات
    'bg_main': '#0A0F23',
    'bg_surface': '#141C36',
    'bg_card_hover': '#1A2444',
    'bg_sidebar': '#06081A', 'bg_sidebar_1': '#0A1030', 'bg_sidebar_2': '#06081A',
    'bg_sidebar_item': '#141C36', 'bg_sidebar_selected_from': '#4F46E5', 'bg_sidebar_selected_to': '#7C3AED',
    'bg_hover_soft': 'rgba(139, 147, 255, 0.14)',
    'bg_active_soft': 'rgba(139, 147, 255, 0.22)',
    # النصوص
    'text_primary': '#F1F5FD', 'text_secondary': '#C3CDE4', 'text_muted': '#5D6B8C',
    'text_inverse': '#0A0F23', 'text_sidebar': '#7D89A8', 'text_sidebar_hover': '#FFFFFF',
    'text_sidebar_selected': '#FFFFFF', 'text_on_primary': '#FFFFFF',
    # الحدود والمدخلات
    'border': '#263252', 'border_light': '#1B2440', 'border_focus': '#8B93FF',
    'border_error': '#F87171',
    'input_bg': '#10182E', 'input_border': '#334165', 'input_focus_border': '#8B93FF',
    'input_placeholder': '#5D6B8C',
    'sidebar_border': 'rgba(139, 147, 255, 0.09)',
    'sidebar_separator': 'rgba(139, 147, 255, 0.08)',
}

RADIUS_SM = '8px'
RADIUS_MD = '12px'
RADIUS_LG = '16px'
RADIUS_XL = '20px'
RADIUS_PILL = '9999px'

FONT_SM = '12px'
FONT_MD = '14px'
FONT_LG = '16px'
FONT_XL = '20px'
FONT_2XL = '24px'

TRANSITION_FAST = '150ms ease'

# الثيم النشط حالياً — تستخدمه الرسوم البيانية وغيره لتكييف الألوان
CURRENT_THEME = 'light'


def set_active_theme(theme: str):
    global CURRENT_THEME
    CURRENT_THEME = 'dark' if str(theme).lower() == 'dark' else 'light'


def chart_colors() -> dict:
    """ألوان جاهزة للرسوم البيانية (matplotlib) متوافقة مع الثيم النشط"""
    if CURRENT_THEME == 'dark':
        return {
            'text': '#C3CDE4', 'muted': '#5D6B8C', 'spine': '#263252',
            'before': '#FB7185', 'after': '#4ADE80', 'axis_label': '#7D89A8',
        }
    return {
        'text': '#1E2A44', 'muted': '#67748E', 'spine': '#E3E8F2',
        'before': '#F87171', 'after': '#34D399', 'axis_label': '#67748E',
    }


def page_card_colors() -> dict:
    """ألوان بطاقات الصفحات المصغّرة متوافقة مع الثيم النشط"""
    if CURRENT_THEME == 'dark':
        return {
            'bg': '#141C36', 'border': '#263252', 'border_sel': '#8B93FF',
            'bg_sel': '#23224E', 'num': '#7D89A8', 'num_sel': '#A5B4FC',
        }
    return {
        'bg': '#FFFFFF', 'border': '#E3E8F2', 'border_sel': '#6366F1',
        'bg_sel': '#EEF2FF', 'num': '#67748E', 'num_sel': '#4F46E5',
    }


def _build(qss: str, c: dict) -> str:
    """يستبدل المتغيرات `{name}` داخل ورقة الأنماط وياكل الأقواس المزدوجة"""
    out = qss
    for key, value in c.items():
        out = out.replace('{' + key + '}', value)
    return out.replace('{{', '{').replace('}}', '}')


_UI_QSS = '''
/* ============ الأساس ============ */
QWidget {{
    font-family: "Cairo", "Tajawal", "Segoe UI", "Tahoma", "Arial";
    font-size: {FONT_MD};
    color: {text_primary};
    background-color: {bg_main};
    selection-background-color: {primary};
    selection-color: {text_inverse};
}}
QMainWindow, QWidget#centralWidget {{
    background-color: {bg_main};
}}
QLabel {{
    background: transparent;
}}

/* ============ الشريط الجانبي ============ */
QWidget#sidebarContainer {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {bg_sidebar_1}, stop:1 {bg_sidebar_2});
    border-left: 1px solid {border_light};
}}
QWidget#sidebarHeader {{
    background: transparent;
    padding: 26px 20px 18px 20px;
    border-bottom: 1px solid {sidebar_separator};
}}
QLabel#appLogo {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {grad_from}, stop:1 {grad_to});
    color: {text_on_primary};
    font-size: 22px;
    border-radius: 14px;
    min-width: 44px;
    min-height: 44px;
    max-width: 44px;
    max-height: 44px;
}}
QLabel#appTitle {{
    color: {text_sidebar_hover};
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 0.3px;
    background: transparent;
}}
QLabel#appSubtitle {{
    color: {text_sidebar};
    font-size: 11.5px;
    background: transparent;
}}
QListWidget#sidebar {{
    background: transparent;
    border: none;
    padding: 10px 12px;
    outline: none;
}}
QListWidget#sidebar::item {{
    color: {text_sidebar};
    padding: 13px 16px;
    border-radius: 14px;
    margin: 4px 6px;
    font-weight: 600;
    font-size: 14px;
    background: transparent;
}}
QListWidget#sidebar::item:hover {{
    background: rgba(255, 255, 255, 0.07);
    color: {text_sidebar_hover};
}}
QListWidget#sidebar::item:selected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {bg_sidebar_selected_from}, stop:1 {bg_sidebar_selected_to});
    color: {text_sidebar_selected};
    font-weight: 800;
}}
QWidget#sidebarFooter {{
    background: transparent;
    border-top: 1px solid {sidebar_separator};
}}
QPushButton#sidebarBtn {{
    background: transparent;
    color: {text_sidebar};
    border: 1px solid {sidebar_border};
    border-radius: 12px;
    font-weight: 600;
    font-size: 13px;
    min-height: 38px;
    padding: 0 14px;
}}
QPushButton#sidebarBtn:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: {text_sidebar_hover};
    border-color: {bg_sidebar_selected_from};
}}
QPushButton#sidebarBtn:pressed {{
    background: rgba(255, 255, 255, 0.14);
}}
QLabel#versionLabel {{
    color: {text_sidebar};
    font-size: 11px;
    padding: 2px;
    font-weight: 400;
    background: transparent;
}}

/* ============ صفحات المحتوى ============ */
QWidget#pageContainer {{
    background-color: {bg_surface};
    border-radius: 22px;
    border: 1px solid {border};
}}
QScrollArea#pageScroll, QScrollArea#pageScroll > QWidget {{
    background: transparent;
    border: none;
}}
QLabel#pageTitle {{
    font-size: 25px;
    font-weight: 800;
    color: {text_primary};
    background: transparent;
}}
QLabel#pageDesc {{
    font-size: 13px;
    color: {text_secondary};
    background: transparent;
}}

/* ============ منطقة السحب والإفلات (الارتفاع يضبطه الكود — min_height) ============ */
QFrame#dropZone {{
    background-color: {primary_light};
    border: 2.5px dashed {input_border};
    border-radius: 22px;
}}
QFrame#dropZone:hover {{
    border-color: {primary};
    background-color: {bg_active_soft};
}}
QLabel#dropIcon {{
    font-size: 52px;
    color: {primary};
    background: transparent;
    margin-bottom: 8px;
}}
QLabel#dropText {{
    color: {text_primary};
    font-size: 15.5px;
    font-weight: 700;
    background: transparent;
}}
QLabel#dropSubtext {{
    color: {text_muted};
    font-size: 12px;
    background: transparent;
}}
QLabel#fileMeta {{
    color: {text_secondary};
    font-weight: 600;
    font-size: 14px;
    padding: 4px 0;
    background: transparent;
}}
QLabel#sectionTitle {{
    color: {text_primary};
    font-weight: 700;
    font-size: 13px;
    background: transparent;
}}
QLabel#hintLabel {{
    color: {text_muted};
    font-size: 12px;
    font-weight: 400;
    background: transparent;
}}
QLabel#accentLabel {{
    color: {primary};
    font-size: 12px;
    font-weight: 700;
    background: transparent;
}}

/* ============ الأزرار ============ */
QPushButton#primaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {grad_from}, stop:1 {grad_to});
    color: {text_on_primary};
    border-radius: 14px;
    font-weight: 700;
    font-size: 14.5px;
    min-height: 46px;
    padding: 0 30px;
    border: none;
    letter-spacing: 0.2px;
}}
QPushButton#primaryBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {grad_hover_from}, stop:1 {grad_hover_to});
    min-height: 47px;
}}
QPushButton#primaryBtn:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {grad_pressed_from}, stop:1 {grad_pressed_to});
    min-height: 46px;
    padding-top: 1px;
}}
QPushButton#primaryBtn:disabled {{
    background-color: {bg_hover_soft};
    color: {text_muted};
}}
QPushButton#secondaryBtn {{
    background-color: {bg_hover_soft};
    color: {text_secondary};
    border: 1.5px solid {border};
    border-radius: 14px;
    font-weight: 600;
    font-size: 13px;
    min-height: 40px;
    padding: 0 20px;
}}
QPushButton#secondaryBtn:hover {{
    color: {text_primary};
    border-color: {primary};
    background-color: {bg_active_soft};
}}
QPushButton#dangerBtn {{
    background-color: transparent;
    color: {error};
    border: 1.5px solid {input_border};
    border-radius: 12px;
    font-weight: 600;
    font-size: 12.5px;
    min-height: 36px;
    padding: 0 16px;
}}
QPushButton#dangerBtn:hover {{
    background-color: {error_bg};
    color: {error_text};
    border-color: {error};
}}
QPushButton#dangerBtn:pressed {{
    background-color: {error_light};
}}
QFrame#optionCard {{
    background-color: {bg_hover_soft};
    border: 2px solid {border};
    border-radius: 16px;
}}
QFrame#optionCard[selected="true"] {{
    background-color: {primary_light};
    border: 2px solid {primary};
}}
QLabel#optionTitle {{
    font-size: 14px;
    font-weight: 800;
    color: {text_primary};
    background: transparent;
}}
QLabel#optionDesc {{
    font-size: 12px;
    color: {text_secondary};
    background: transparent;
}}
QLabel#statusSuccess {{
    background-color: {success_bg};
    border: 1.5px solid {success_border};
    border-radius: 14px;
    padding: 14px 16px;
    font-size: 13px;
    font-weight: 600;
    color: {success_text};
}}
QLabel#statusError {{
    background-color: {error_bg};
    border: 1.5px solid {error_border};
    border-radius: 14px;
    padding: 14px 16px;
    font-size: 13px;
    font-weight: 600;
    color: {error_text};
}}

/* ============ قائمة الملفات ============ */
QListWidget#fileList {{
    background-color: {input_bg};
    border: 1.5px solid {border};
    border-radius: 16px;
    padding: 8px;
    outline: none;
    font-size: 13px;
}}
QListWidget#fileList::item {{
    color: {text_secondary};
    background: {bg_hover_soft};
    border-radius: 10px;
    padding: 10px 14px;
    margin: 4px 2px;
    font-weight: 600;
}}
QListWidget#fileList::item:hover {{
    background: {bg_active_soft};
    color: {text_primary};
}}
QListWidget#fileList::item:selected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {grad_from}, stop:1 {grad_to});
    color: {text_on_primary};
}}

/* ============ المدخلات ============ */
QLineEdit {{
    background-color: {input_bg};
    border: 1.5px solid {input_border};
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 14px;
    color: {text_primary};
}}
QLineEdit:hover {{
    border-color: {primary};
}}
QLineEdit:focus {{
    border: 2px solid {input_focus_border};
    padding: 9px 13px;
}}
QLineEdit:disabled {{
    background-color: {bg_hover_soft};
    color: {text_muted};
    border-color: {border};
}}
QTextEdit {{
    background-color: {input_bg};
    border: 1.5px solid {input_border};
    border-radius: 12px;
    padding: 8px;
    color: {text_primary};
}}
QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {input_placeholder};
}}

/* ============ الاختيارات ============ */
QRadioButton {{
    color: {text_secondary};
    font-weight: 600;
    spacing: 8px;
    background: transparent;
}}
QRadioButton::indicator {{
    width: 18px; height: 18px;
    border: 2px solid {input_border};
    border-radius: 10px;
    background: {input_bg};
}}
QRadioButton::indicator:hover {{
    border-color: {primary};
}}
QRadioButton::indicator:checked {{
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.4, fx:0.5, fy:0.5,
        stop:0 {primary}, stop:1 {primary});
    border: 2px solid {primary};
}}
QCheckBox {{
    color: {text_secondary};
    font-weight: 600;
    spacing: 8px;
    background: transparent;
}}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border: 2px solid {input_border};
    border-radius: 5px;
    background: {input_bg};
}}
QCheckBox::indicator:hover {{
    border-color: {primary};
}}
QCheckBox::indicator:checked {{
    background: {primary};
    border-color: {primary};
    image: url(none);
}}
QCheckBox:disabled {{
    color: {text_muted};
}}

/* ============ شريط التقدم ============ */
QProgressBar {{
    background-color: {bg_hover_soft};
    border-radius: 10px;
    border: 1px solid {border};
    height: 12px;
    text-align: center;
    color: transparent;
    font-size: 9px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {grad_from}, stop:1 {grad_to});
    border-radius: 8px;
    margin: 1.5px;
}}

/* ============ أشرطة التمرير ============ */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {input_border};
    border-radius: 5px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{
    background: {primary};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background: {input_border};
    border-radius: 5px;
    min-width: 32px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {primary};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QScrollArea {{
    background: transparent;
    border: 1.5px solid {border};
    border-radius: 14px;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

/* ============ الحوارات ============ */
QMessageBox {{
    background-color: {bg_surface};
}}
QMessageBox QLabel {{
    color: {text_primary};
    font-size: 14px;
    background: transparent;
}}
QMessageBox QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {grad_from}, stop:1 {grad_to});
    color: {text_on_primary};
    border-radius: 10px;
    font-weight: 700;
    min-height: 36px;
    min-width: 90px;
    padding: 0 18px;
}}
QMessageBox QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {grad_hover_from}, stop:1 {grad_hover_to});
}}
QToolTip {{
    background-color: {bg_sidebar};
    color: {text_sidebar_hover};
    border: 1px solid {border_focus};
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 500;
}}
'''


def get_style(theme: str = "auto") -> str:
    """يعيد ورقة الأنماط الكاملة للثيم المطلوب"""
    theme = str(theme).lower()
    if theme == "dark":
        set_active_theme("dark")
        c = DARK_COLORS
    else:
        set_active_theme("light")
        c = LIGHT_COLORS
    tokens = {**c, "FONT_MD": FONT_MD}
    return _build(_UI_QSS, tokens)
