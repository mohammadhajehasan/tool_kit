"""أيقونات SVG خفيفة مضمّنة — بديل عن الرموز التعبيرية في الشريط الجانبي."""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QByteArray, Qt, QSize
from PySide6.QtSvg import QSvgRenderer


# مسارات Lucide-style مبسّطة (stroke-based)
_SVGS = {
    "compress": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M8 3v3a2 2 0 0 1-2 2H3"/><path d="M21 8h-3a2 2 0 0 1-2-2V3"/>
 <path d="M3 16h3a2 2 0 0 1 2 2v3"/><path d="M16 21v-3a2 2 0 0 1 2-2h3"/>
</svg>""",
    "split": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/>
 <path d="M20 4 8.12 15.88"/><path d="M14.47 14.48 20 20"/><path d="M8.12 8.12 12 12"/>
</svg>""",
    "merge": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="m8 6 4-4 4 4"/><path d="M12 2v10.3"/><path d="m8 18 4 4 4-4"/>
 <path d="M12 22V12"/><path d="M2 12h20"/>
</svg>""",
    "images": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
 <circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
</svg>""",
    "pdf_images": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
 <polyline points="14 2 14 8 20 8"/><circle cx="10" cy="13" r="2"/>
 <path d="m20 17-1.09-1.09a2 2 0 0 0-2.82 0L10 20"/>
</svg>""",
    "archive": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/>
 <path d="M10 12h4"/>
</svg>""",
    "protect": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
 <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
</svg>""",
    "watermark": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
 <path d="m9 12 2 2 4-4"/>
</svg>""",
    "organize": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <rect width="6" height="6" x="3" y="3" rx="1"/><rect width="6" height="6" x="15" y="3" rx="1"/>
 <rect width="6" height="6" x="3" y="15" rx="1"/><rect width="6" height="6" x="15" y="15" rx="1"/>
</svg>""",
    "info": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
</svg>""",
    "developer": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
</svg>""",
    "ocr": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M4 7V4h3"/><path d="M20 7V4h-3"/><path d="M4 17v3h3"/><path d="M20 17v3h-3"/>
 <path d="M9 12h6"/><path d="M12 9v6"/>
</svg>""",
    "export": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
 <polyline points="14 2 14 8 20 8"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/>
</svg>""",
    "diff": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/>
 <path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>
 <path d="M7 12h10"/>
</svg>""",
    "ai": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/>
 <path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>
</svg>""",
    "app": """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
 fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
 <polyline points="14 2 14 8 20 8"/>
</svg>""",
}


def svg_icon(name: str, color: str = "#A3AEC8", size: int = 20) -> QIcon:
    """يبني QIcon من SVG مضمّن بالاسم واللون المحددين."""
    template = _SVGS.get(name)
    if not template:
        return QIcon()
    data = template.format(color=color).encode("utf-8")
    renderer = QSvgRenderer(QByteArray(data))
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return QIcon(pm)
