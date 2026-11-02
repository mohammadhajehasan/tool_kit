"""
توليد أيقونة احترافية وجميلة لتطبيق "أداة PDF"
- خلفية متدرجة (أرجواني → نيلي) مع توهج
- مستند PDF أبيض برواز
- حرف PDF بخط عريض
- أضواء/نجوم صغيرة للتفاصيل
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_icon(size: int = 256) -> Image.Image:
    """يرسم أيقونة التطبيق بحجم معين."""
    # عوامل للقياس (لأي حجم)
    s = size / 256.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ===== 1. خلفية متدرجة (أرجواني → نيلي) =====
    for y in range(size):
        t = y / size
        r = int(79 + (99 - 79) * t)      # 79 → 99
        g = int(70 + (102 - 70) * t)     # 70 → 102
        b = int(229 + (241 - 229) * t)   # 229 → 241
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # ===== 2. توهج علوي =====
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse(
        [int(40 * s), int(-50 * s), int(216 * s), int(126 * s)],
        fill=(167, 139, 250, 70),   # #a78bfa بشفافية
    )
    img = Image.alpha_composite(img, glow)

    # ===== 3. دائرة حدود شفافة مضيئة (اختياري) =====
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse(
        [int(18 * s), int(18 * s), int(238 * s), int(238 * s)],
        outline=(255, 255, 255, 60), width=int(3 * s),
    )
    img = Image.alpha_composite(img, ring)

    # ===== 4. مستند PDF أبيض =====
    doc_w, doc_h = int(150 * s), int(190 * s)
    dx = (size - doc_w) // 2
    dy = (size - doc_h) // 2

    # ظل خلف المستند
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [dx + int(6 * s), dy + int(8 * s), dx + doc_w + int(6 * s), dy + doc_h + int(8 * s)],
        radius=int(22 * s), fill=(15, 23, 42, 90),
    )
    img = Image.alpha_composite(img, shadow)

    # المستند الأبيض
    doc_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dd = ImageDraw.Draw(doc_layer)
    dd.rounded_rectangle(
        [dx, dy, dx + doc_w, dy + doc_h],
        radius=int(22 * s), fill=(255, 255, 255, 255),
    )
    # ثنية (اقلب) الزاوية أعلى اليمين
    fold_x = dx + doc_w
    fold_y = dy
    fold_size = int(36 * s)
    dd.polygon(
        [
            (fold_x, fold_y),
            (fold_x - fold_size, fold_y),
            (fold_x, fold_y + fold_size),
        ],
        fill=(226, 232, 240, 255),  # #e2e8f0
    )
    img = Image.alpha_composite(img, doc_layer)

    # ===== 5. خطوط نصية داخل المستند =====
    lines_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lines_layer)

    # سطر عنوان أرجواني
    ld.rounded_rectangle(
        [dx + int(18 * s), dy + int(22 * s), dx + int(60 * s), dy + int(32 * s)],
        radius=int(5 * s), fill=(99, 102, 241, 255),  # #6366f1
    )

    # خطوط سوداء فاتحة
    for i in range(4):
        ly = dy + int(50 * s) + i * int(18 * s)
        lw = int(114 * s) - (i * int(18 * s))
        ld.rounded_rectangle(
            [dx + int(18 * s), ly, dx + int(18 * s) + lw, ly + int(8 * s)],
            radius=int(4 * s), fill=(148, 163, 184, 180),  # #94a3b8
        )

    # خط قصير أسفل
    ld.rounded_rectangle(
        [dx + int(18 * s), dy + int(122 * s), dx + int(90 * s), dy + int(130 * s)],
        radius=int(4 * s), fill=(148, 163, 184, 180),
    )

    # أيقونة صورة (جبل وشمس) داخل المستند
    pic_x = dx + int(18 * s)
    pic_y = dy + int(142 * s)
    pic_w = int(114 * s)
    pic_h = int(28 * s)
    ld.rounded_rectangle(
        [pic_x, pic_y, pic_x + pic_w, pic_y + pic_h],
        radius=int(8 * s), fill=(224, 231, 255, 255),  # #e0e7ff
    )
    # جبل صغير
    ld.polygon(
        [
            (pic_x + int(25 * s), pic_y + pic_h - int(4 * s)),
            (pic_x + int(48 * s), pic_y + int(8 * s)),
            (pic_x + int(72 * s), pic_y + pic_h - int(4 * s)),
        ],
        fill=(99, 102, 241, 220),
    )
    ld.polygon(
        [
            (pic_x + int(55 * s), pic_y + pic_h - int(4 * s)),
            (pic_x + int(75 * s), pic_y + int(12 * s)),
            (pic_x + int(95 * s), pic_y + pic_h - int(4 * s)),
        ],
        fill=(139, 92, 246, 220),  # #8b5cf6
    )
    # شمس صغيرة
    ld.ellipse(
        [pic_x + int(84 * s), pic_y + int(2 * s), pic_x + int(94 * s), pic_y + int(12 * s)],
        fill=(251, 192, 45, 255),  # #fbc02d
    )

    img = Image.alpha_composite(img, lines_layer)

    # ===== 6. نص "PDF" كبير أسفل المستند (شعار) =====
    # استخدم خط عريض — نبحث عن خط مناسب
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold
        "C:/Windows/Fonts/segoeuib.ttf",     # Segoe UI Bold
        "C:/Windows/Fonts/impact.ttf",        # Impact
        "C:/Windows/Fonts/arial.ttf",
    ]
    font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_path = fp
            break

    try:
        if font_path:
            # حجم يتناسب
            font_size = int(46 * s)
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    text = "PDF"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]

    text_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)

    # نص أبيض مظلل
    tx = (size - tw) // 2 - bbox[0]
    ty = dy + doc_h + int(18 * s) - bbox[1]

    td.text((tx + int(2 * s), ty + int(2 * s)), text, font=font, fill=(15, 23, 42, 140))
    td.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

    img = Image.alpha_composite(img, text_layer)

    # ===== 7. نجوم/نقاط مضيئة =====
    stars_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd2 = ImageDraw.Draw(stars_layer)
    stars = [
        (int(42 * s), int(36 * s), int(4 * s)),
        (int(212 * s), int(60 * s), int(3 * s)),
        (int(28 * s), int(150 * s), int(3 * s)),
        (int(226 * s), int(168 * s), int(4 * s)),
        (int(50 * s), int(214 * s), int(2 * s)),
        (int(200 * s), int(220 * s), int(3 * s)),
    ]
    for sx, sy, sr in stars:
        sd2.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, 200))

    img = Image.alpha_composite(img, stars_layer)

    return img


def main():
    # إنشاء مجلد resources/icons إن لم يكن موجوداً
    icon_dir = os.path.join("resources", "icons")
    os.makedirs(icon_dir, exist_ok=True)

    # إنشاء صورة 256x256 كأساس
    img = create_icon(256)

    # حفظ PNG للعرض والاستخدام الداخلي
    png_path = os.path.join(icon_dir, "app.png")
    img.save(png_path)

    # إنشاء أيقونات متعددة الأحجام لـ ICO
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(os.path.join(icon_dir, "app.ico"), sizes=sizes)

    print(f"✅ تم توليد الأيقونة:")
    print(f"   - {os.path.abspath(png_path)}")
    print(f"   - {os.path.abspath(os.path.join(icon_dir, 'app.ico'))}")


if __name__ == "__main__":
    main()