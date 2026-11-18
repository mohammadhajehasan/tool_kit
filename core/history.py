"""سجل النشاط والإحصائيات — يُخزَّن في settings.json بجانب التطبيق."""

import datetime
import json
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(_BASE, "settings.json")


def _load() -> dict:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # التسجيل اختياري — لا نعطل العملية بسبب فشل الحفظ


def record(tool: str, path: str, saved_bytes: int = 0):
    """يسجّل عملية ناجحة: الأداة، الملف، والمساحة الموفّرة (للضغط)."""
    data = _load()
    stats = data.setdefault("stats", {"processed": 0, "saved_bytes": 0})
    stats["processed"] = int(stats.get("processed", 0)) + 1
    try:
        stats["saved_bytes"] = int(stats.get("saved_bytes", 0)) + max(0, int(saved_bytes or 0))
    except (TypeError, ValueError):
        pass

    recent = data.setdefault("recent", [])
    recent.insert(0, {
        "tool": tool,
        "path": path,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    seen, uniq = set(), []
    for r in recent:
        key = r.get("path")
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    data["recent"] = uniq[:8]
    _save(data)


def get_activity() -> dict:
    """يعرج الإحصائيات وآخر الملفات للعرض."""
    data = _load()
    stats = data.get("stats", {"processed": 0, "saved_bytes": 0})
    return {
        "processed": int(stats.get("processed", 0)),
        "saved_bytes": int(stats.get("saved_bytes", 0)),
        "recent": list(data.get("recent", [])),
    }


def format_size(num_bytes: int) -> str:
    size = float(max(0, num_bytes))
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
