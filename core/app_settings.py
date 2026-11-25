"""مسار موحّد لإعدادات التطبيق — قابل للكتابة أيضاً داخل exe المجمّع.

في نسخة PyInstaller onefile يكون مجلد المصدر مؤقتاً ويُحذف عند الإغلاق،
لذلك نحفظ الإعدادات في %LOCALAPPDATA%\\PDF_Toolbox عند التجميد.
"""

import json
import os
import sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_SETTINGS = os.path.join(APP_DIR, "settings.json")


def _user_dir() -> str:
    if getattr(sys, "frozen", False):
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PDF_Toolbox")
    return APP_DIR


SETTINGS_PATH = os.path.join(_user_dir(), "settings.json")


def load() -> dict:
    """يقرأ الإعدادات (ملف المصدر ثم ملف المستخدم يعلو عليه)."""
    data: dict = {}
    seen = set()
    for path in (SOURCE_SETTINGS, SETTINGS_PATH):
        if not path or path in seen:
            continue
        seen.add(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                data.update(loaded)
        except Exception:
            continue
    return data


def save(updates: dict) -> None:
    """يدمج قيماً جديدة في ملف الإعدادات القابل للكتابة."""
    data = {}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            data = loaded
    except Exception:
        data = {}
    data.update(updates or {})
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
