"""عميل Unlimited-OCR (Baidu) عبر خادم SGLang/vLLM متوافق مع OpenAI.

المسار: PDF ← صور صفحات ← ``POST {base}/v1/chat/completions`` بصيغة
``"<PAGE><image>" * n + "Multi page parsing."`` ← نص منظم لكل صفحة.

ينتج دائماً ملف TXT، ويبني PDF قابلاً للبحث بطبقة نص مخفية فوق الصفحات
الأصلية (بدون إعادة ضغط الصور). إن تعذّر بناء الطبقة يبقى TXT كافياً.
"""

from __future__ import annotations

import base64
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from core import app_settings

DEFAULTS = {
    "unlimited_ocr_url": "http://127.0.0.1:10000",
    "unlimited_ocr_model": "Unlimited-OCR-2",
    "unlimited_ocr_api_key": "",
    "unlimited_ocr_dpi": 200,
    "unlimited_ocr_pages_per_request": 4,
    "unlimited_ocr_tokens_per_page": 8000,
    "unlimited_ocr_crop_mode": True,
    "unlimited_ocr_ngram": False,
    "unlimited_ocr_ai_ocr": True,
}

# النموذج لا يخرج Markdown بل كتل تخطيط: <BLOCK>label<LEVELn>[x1,y1,x2,y2]<FORK>...
_PAGE_RE = re.compile(r"<\s*/?\s*PAGE\s*\d*\s*>", re.I)
_BLOCK_HEAD_RE = re.compile(
    r"<\s*BLOCK\s*>\s*([A-Za-z_][A-Za-z_0-9]*)"
    r"(?:\s*<\s*LEVEL\s*(\d*)\s*[>}]?)?"
    r"(?:\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)[^\]]*\])?"
    r"(?:\s*<\s*LEVEL\s*(\d*)\s*[>}]?)?"
    r"(?:\s*<\s*FORK\s*>)?",
    re.I,
)
_BBOX_RE = re.compile(r"\[\s*-?\d+(?:\s*,\s*-?\d+){3,}[^\]]*\]")
_TOKEN_RE = re.compile(
    r"<\s*/?\s*(?:PAGE|BLOCK|FORK|MERGE)\s*\d*\s*>"
    r"|<\s*/?\s*LEVEL\s*\d*\s*[>}]?"
    r"|<\s*image\s*>",
    re.I,
)
_TAG_RE = re.compile(r"<[^<>\n]{1,80}>")
_SKIP_LABELS = {"image", "figure", "picture", "chart", "img", "seal"}


class UnlimitedOcrError(Exception):
    pass


@dataclass
class Block:
    label: str
    level: int | None
    bbox: tuple[int, int, int, int] | None
    text: str


@dataclass
class Page:
    blocks: list[Block] = field(default_factory=list)
    error: str = ""

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks if b.text).strip()


# ================= الإعدادات =================

def load_config() -> dict:
    cfg = dict(DEFAULTS)
    cfg.update(app_settings.load())
    return cfg


def save_config(updates: dict) -> None:
    app_settings.save(updates)


def is_configured(cfg: dict | None = None) -> bool:
    cfg = cfg or load_config()
    return bool(str(cfg.get("unlimited_ocr_url") or "").strip()
                and str(cfg.get("unlimited_ocr_model") or "").strip())


def _base_root(base_url: str) -> str:
    root = (base_url or "").strip().rstrip("/")
    if not root:
        raise UnlimitedOcrError("Unlimited-OCR غير مُعدّ: أدخل عنوان الخادم واسم النموذج")
    if not re.match(r"^https?://", root, re.I):
        root = "http://" + root
    if not re.search(r"/v1$", root) and "/v1/" not in root:
        root += "/v1"
    return root


def _headers(api_key: str) -> dict:
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    key = (api_key or "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


# ================= فحص الاتصال =================

def check_connection(base_url: str, api_key: str = "", timeout: float = 8.0) -> dict:
    """يتحقق من خادم OpenAI-compatible ويعيد قائمة النماذج المتاحة."""
    url = _base_root(base_url) + "/models"
    req = urllib.request.Request(url, headers=_headers(api_key), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        raise UnlimitedOcrError(f"خطأ من خادم Unlimited-OCR ({e.code}): {body}") from e
    except urllib.error.URLError as e:
        raise UnlimitedOcrError(f"تعذّر الاتصال بخادم Unlimited-OCR: {e.reason}") from e
    except Exception as e:
        raise UnlimitedOcrError(f"تعذّر الاتصال بخادم Unlimited-OCR: {e}") from e

    models = []
    raw = data.get("data") if isinstance(data, dict) else None
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get("id"):
                models.append(str(item["id"]))
    return {"url": url, "models": models}


# ================= التحويل إلى صور =================

def _render_pages(pdf_path: str, dpi: int, cancel_check=None) -> list[bytes]:
    try:
        import fitz
    except ImportError as e:
        raise UnlimitedOcrError("PyMuPDF غير مثبّت. ثبّته: pip install pymupdf") from e
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"الملف غير موجود: {pdf_path}")

    doc = fitz.open(pdf_path)
    images: list[bytes] = []
    try:
        zoom = max(72, int(dpi or 200)) / 72.0
        mat = fitz.Matrix(zoom, zoom)
        for page in doc:
            if cancel_check and cancel_check():
                raise InterruptedError("تم إلغاء العملية")
            pix = page.get_pixmap(matrix=mat, alpha=False)
            try:
                data = pix.tobytes("jpeg", jpg_quality=90)
            except TypeError:  # إصدارات أقدم
                data = pix.tobytes("jpg")
            images.append(data)
    finally:
        doc.close()
    if not images:
        raise UnlimitedOcrError("لا توجد صفحات للمعالجة")
    return images


# ================= طلب الخادم =================

def _processor_str() -> str:
    """سلسلة معالج SGLang المخصص — تُبنى فقط إن كانت sglang مثبتة محلياً."""
    try:
        from sglang.srt.sampling.custom_logit_processor import (  # type: ignore
            DeepseekOCRNoRepeatNGramLogitProcessor,
        )
        return DeepseekOCRNoRepeatNGramLogitProcessor.to_str()
    except Exception:
        return ""


def _build_payload(images: list[bytes], cfg: dict, max_tokens: int | None = None) -> dict:
    content = []
    for data in images:
        b64 = base64.b64encode(data).decode("ascii")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        })
    content.append({
        "type": "text",
        "text": "<PAGE><image>" * len(images) + "Multi page parsing.",
    })
    tokens_per_page = int(cfg.get("unlimited_ocr_tokens_per_page") or 8000)
    payload = {
        "model": str(cfg.get("unlimited_ocr_model") or "Unlimited-OCR-2"),
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max(1, int(max_tokens or tokens_per_page * len(images))),
        "temperature": 0,
        "skip_special_tokens": False,
        "images_config": {"crop_mode": bool(cfg.get("unlimited_ocr_crop_mode", True))},
        "stream": True,
    }
    if cfg.get("unlimited_ocr_ngram"):
        processor = _processor_str()
        if processor:
            payload["custom_logit_processor"] = processor
            payload["custom_params"] = {
                "ngram_size": 35,
                "window_size": 1024 if len(images) > 1 else 128,
                "page_token_id": 128827,
                "eos_token_id": 1,
                "max_page_tokens": 20000,
            }
    return payload


_TOKEN_COUNTS_RE = re.compile(
    r"total of\s+(\d+)\s+tokens:\s*(\d+)\s+tokens from the input messages"
    r"\s+and\s+(\d+)\s+tokens for the completion",
    re.I,
)


def _post_once(url: str, payload: dict, api_key: str, timeout: float, cancel_check=None) -> str:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_headers(api_key),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "text/event-stream" not in ctype and "ndjson" not in ctype:
                # خادم لم يستخدم البث: استجابة JSON واحدة
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    data = json.loads(raw)
                    return (data["choices"][0]["message"].get("content") or "")
                except Exception:
                    return _parse_sse_text(raw)

            chunks: list[str] = []
            for raw in resp:
                if cancel_check and cancel_check():
                    raise InterruptedError("تم إلغاء العملية")
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                if line.startswith("data:"):
                    line = line[5:].strip()
                if line == "[DONE]":
                    break
                try:
                    event = json.loads(line)
                except Exception:
                    continue
                for choice in event.get("choices") or []:
                    delta = (choice.get("delta") or {}).get("content")
                    if delta:
                        chunks.append(delta)
            return "".join(chunks)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise _HttpFailure(e.code, body) from e
    except urllib.error.URLError as e:
        raise UnlimitedOcrError(f"تعذّر الاتصال بخادم Unlimited-OCR: {e.reason}") from e
    except InterruptedError:
        raise
    except Exception as e:
        raise UnlimitedOcrError(f"تعذّر الاتصال بخادم Unlimited-OCR: {e}") from e


class _HttpFailure(Exception):
    def __init__(self, code: int, body: str):
        super().__init__(f"HTTP {code}: {body[:400]}")
        self.code = code
        self.body = body


def _parse_sse_text(text: str) -> str:
    chunks = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue
        try:
            event = json.loads(data)
        except Exception:
            continue
        for choice in event.get("choices") or []:
            delta = (choice.get("delta") or {}).get("content")
            if delta:
                chunks.append(delta)
    return "".join(chunks)


def _request_batch(images: list[bytes], cfg: dict, api_key: str,
                   timeout: float, cancel_check=None) -> str:
    url = _base_root(str(cfg.get("unlimited_ocr_url") or "")) + "/chat/completions"
    payload = _build_payload(images, cfg)
    attempts = 0
    while True:
        attempts += 1
        if cancel_check and cancel_check():
            raise InterruptedError("تم إلغاء العملية")
        try:
            text = _post_once(url, payload, api_key, timeout, cancel_check)
            if not text.strip() and attempts < 2:
                continue
            return text
        except _HttpFailure as e:
            body = e.body or ""
            if attempts == 1:
                match = _TOKEN_COUNTS_RE.search(body)
                if match and e.code in (400, 413):
                    limit = int(match.group(1)) - int(match.group(2)) - 64
                    if limit > 0:
                        payload["max_tokens"] = max(1, limit)
                        continue
                if "custom_logit_processor" in body or "custom_params" in body:
                    payload.pop("custom_logit_processor", None)
                    payload.pop("custom_params", None)
                    continue
            raise UnlimitedOcrError(
                f"خطأ من خادم Unlimited-OCR ({e.code}): {body[:400]}"
            ) from e


# ================= تحليل المخرجات =================

def _clean_fragment(text: str) -> str:
    text = re.sub(r"<\s*/\s*table\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<\s*table\b[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<\s*/\s*tr\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<\s*tr\b[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<\s*(?:td|th)\b[^>]*>", " | ", text, flags=re.I)
    text = re.sub(r"<\s*/\s*(?:td|th)\s*>", " ", text, flags=re.I)
    text = _TOKEN_RE.sub("\n", text)
    text = _BBOX_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)

    lines = []
    for line in text.splitlines():
        line = re.sub(r"[\t\u00a0 ]+", " ", line).strip()
        line = re.sub(r"^(\|\s*)+", "", line)
        line = re.sub(r"(\s*\|)+$", "", line)
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def parse_pages(raw: str, expected_pages: int = 0) -> list[Page]:
    """يقسم مخرجات النموذج على <PAGE> ويحوّل كل صفحة إلى كتل نصية."""
    segments = _PAGE_RE.split(raw or "")
    if segments and not segments[0].strip():
        segments.pop(0)
    if not segments:
        segments = [raw or ""]

    pages: list[Page] = []
    for seg in segments:
        blocks: list[Block] = []
        heads = list(_BLOCK_HEAD_RE.finditer(seg))
        if not heads:
            cleaned = _clean_fragment(seg)
            if cleaned:
                blocks.append(Block("text", None, None, cleaned))
        else:
            for i, match in enumerate(heads):
                end = heads[i + 1].start() if i + 1 < len(heads) else len(seg)
                label = (match.group(1) or "text").lower()
                level = match.group(2) or match.group(7)
                level = int(level) if level and level.isdigit() else None
                bbox = None
                if match.group(3) is not None:
                    bbox = tuple(int(match.group(k)) for k in (3, 4, 5, 6))  # type: ignore[assignment]
                body = _clean_fragment(seg[match.end():end])
                if not body:
                    continue
                if label in _SKIP_LABELS and body.strip(" []()") in ("", "image", "figure"):
                    continue
                if label == "title" or label.startswith("title"):
                    body = "#" * max(1, level or 1) + " " + body
                blocks.append(Block(label, level, bbox, body))
        pages.append(Page(blocks))

    if expected_pages > 0:
        while len(pages) < expected_pages:
            pages.append(Page())
        pages = pages[:expected_pages]
    return pages


def pages_to_text(pages: list[Page]) -> str:
    parts = []
    for i, page in enumerate(pages):
        body = page.text
        if body:
            parts.append(f"--- صفحة {i + 1} ---\n{body}")
    return "\n\n".join(parts).strip()


# ================= طبقة النص المخفية =================

def _find_arabic_font() -> str | None:
    windir = os.environ.get("WINDIR") or r"C:\Windows"
    candidates = [
        os.path.join(windir, "Fonts", name)
        for name in ("segoeui.ttf", "arial.ttf", "tahoma.ttf",
                     "NotoSansArabic-Regular.ttf", "DejaVuSans.ttf")
    ]
    try:
        import matplotlib  # type: ignore
        candidates.append(os.path.join(
            os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"))
    except Exception:
        pass
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


_FONT_CACHE: dict[str, str] = {}


def _register_font(font_path: str) -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    name = "UOCR" + str(abs(hash(font_path)) % 10_000_000)
    if name not in _FONT_CACHE:
        pdfmetrics.registerFont(TTFont(name, font_path))
        _FONT_CACHE[name] = font_path
    return name


def _has_rtl(text: str) -> bool:
    return any("\u0590" <= ch <= "\u08ff" or "\ufb50" <= ch <= "\ufeff" for ch in text)


def _visual(line: str) -> str:
    """يرتّب السطر بصرياً (يسار→يمين) ليبقى النص المنطقي قابلاً للبحث."""
    if not line or not _has_rtl(line):
        return line
    try:
        from bidi.algorithm import get_display
        return get_display(line)
    except Exception:
        return line[::-1]


def _wrap_lines(text: str, font_name: str, size: float, max_width: float) -> list[str]:
    from reportlab.pdfbase import pdfmetrics
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for word in paragraph.split():
            trial = (current + " " + word).strip()
            # إعادة الترتيب البصري لا تغيّر مجموع عروض الكلمات، فنقيس النص المنطقي مباشرة
            width = pdfmetrics.stringWidth(trial, font_name, size)
            if current and width > max_width:
                lines.append(current)
                current = word
            else:
                current = trial
            if len(current) > 4000:  # حماية من كتلة ضخمة بلا مسافات
                lines.append(current[:2000])
                current = current[2000:]
        if current:
            lines.append(current)
    return lines


def _fit_block(text: str, font_name: str, width: float, height: float):
    for size in (10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0):
        lines = _wrap_lines(text, font_name, size, max(20.0, width))
        leading = size * 1.22
        if len(lines) * leading <= height or size <= 4.0:
            return size, leading, lines
    return 4.0, 4.9, _wrap_lines(text, font_name, 4.0, max(20.0, width))


def _overlay_bytes(pages: list[Page], sizes: list[tuple[float, float]],
                   font_path: str) -> bytes:
    from reportlab.pdfgen import canvas

    font_name = _register_font(font_path)
    buf = io.BytesIO()
    first = sizes[0] if sizes else (595.0, 842.0)
    c = canvas.Canvas(buf, pagesize=first)

    for idx, page in enumerate(pages):
        width, height = sizes[idx] if idx < len(sizes) else first
        c.setPageSize((width, height))
        cursor_top = 40.0
        for block in page.blocks:
            text = re.sub(r"^#+\s*", "", block.text, flags=re.M).strip()
            if not text:
                continue
            if block.label in _SKIP_LABELS:
                continue
            if block.bbox:
                x0, y0, x1, y1 = block.bbox
                left = max(0.0, min(width, x0 / 1000.0 * width))
                top = max(0.0, min(height, y0 / 1000.0 * height))
                right = max(left + 20.0, min(width, x1 / 1000.0 * width))
                bottom = max(top + 12.0, min(height, y1 / 1000.0 * height))
            else:
                left, right = 40.0, max(60.0, width - 40.0)
                top = cursor_top
                bottom = max(top + 12.0, height - 30.0)
            avail_w = max(20.0, right - left)
            avail_h = max(12.0, bottom - top)
            size, leading, lines = _fit_block(text, font_name, avail_w, avail_h)
            c.setFont(font_name, size)
            y = height - top - size
            for line in lines:
                if y < 6.0:
                    break
                if line:
                    c.drawString(left, y, _visual(line))
                y -= leading
            if not block.bbox:
                cursor_top = height - y + leading * 0.4
        c.showPage()
    c.save()
    return buf.getvalue()


def _page_sizes(pdf_path: str) -> list[tuple[float, float]]:
    import fitz
    doc = fitz.open(pdf_path)
    try:
        return [(float(p.mediabox.width), float(p.mediabox.height)) for p in doc]
    finally:
        doc.close()


def write_searchable_pdf(src_path: str, out_path: str, pages: list[Page],
                         cancel_check=None) -> bool:
    """يدمج طبقة نص مخفية فوق الصفحات الأصلية. يعيد False إن تعذّر."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return False

    font_path = _find_arabic_font()
    if not font_path:
        return False

    sizes = _page_sizes(src_path)
    if cancel_check and cancel_check():
        raise InterruptedError("تم إلغاء العملية")
    overlay = _overlay_bytes(pages, sizes, font_path)
    overlay_reader = PdfReader(io.BytesIO(overlay))
    reader = PdfReader(src_path)
    try:
        if reader.is_encrypted:
            reader.decrypt("")
    except Exception:
        pass

    writer = PdfWriter()
    count = min(len(reader.pages), len(overlay_reader.pages))
    for i in range(count):
        page = reader.pages[i]
        page.merge_page(overlay_reader.pages[i], over=True)
        writer.add_page(page)
    with open(out_path, "wb") as f:
        writer.write(f)
    return True


# ================= الواجهة العامة =================

def _batch_label(start: int, end: int, total: int) -> str:
    return f"⏳ جارٍ استخراج النص عبر Unlimited-OCR… الصفحة {start}/{total}" if start == end \
        else f"⏳ جارٍ استخراج النص عبر Unlimited-OCR… الصفحات {start}-{end}/{total}"


def extract_pages(pdf_path: str, cfg: dict | None = None, *,
                  dpi: int | None = None, cancel_check=None,
                  progress=None) -> list[Page]:
    """يرسل صفحات PDF إلى الخادم ويعيد نصاً منظماً لكل صفحة."""
    cfg = cfg or load_config()
    if not is_configured(cfg):
        raise UnlimitedOcrError("Unlimited-OCR غير مُعدّ: أدخل عنوان الخادم واسم النموذج")
    if cancel_check and cancel_check():
        raise InterruptedError("تم إلغاء العملية")

    images = _render_pages(pdf_path, int(dpi or cfg.get("unlimited_ocr_dpi") or 200), cancel_check)
    api_key = str(cfg.get("unlimited_ocr_api_key") or "")
    timeout = float(cfg.get("unlimited_ocr_timeout") or 900)
    batch_size = max(1, int(cfg.get("unlimited_ocr_pages_per_request") or 4))
    total = len(images)
    parsed_by_page: list[Page | None] = [None] * total
    errors: list[str] = []

    index = 0
    while index < total:
        if cancel_check and cancel_check():
            raise InterruptedError("تم إلغاء العملية")
        chunk = images[index:index + batch_size]
        start, end = index + 1, index + len(chunk)
        if progress:
            progress(_batch_label(start, end, total))
        try:
            raw = _request_batch(chunk, cfg, api_key, timeout, cancel_check)
            parsed = parse_pages(raw, expected_pages=len(chunk))
            for offset in range(len(chunk)):
                parsed_by_page[index + offset] = parsed[offset]
        except InterruptedError:
            raise
        except Exception as e:
            if len(chunk) == 1:
                errors.append(f"صفحة {start}: {e}")
            else:
                # فشل الدفعة: أعد المحاولة صفحة بصفحة لعزل الصفحة المعطلة
                for offset, image in enumerate(chunk):
                    if cancel_check and cancel_check():
                        raise InterruptedError("تم إلغاء العملية")
                    page_no = index + offset + 1
                    if progress:
                        progress(_batch_label(page_no, page_no, total))
                    try:
                        raw = _request_batch([image], cfg, api_key, timeout, cancel_check)
                        single = parse_pages(raw, expected_pages=1)
                        parsed_by_page[index + offset] = single[0]
                    except InterruptedError:
                        raise
                    except Exception as inner:
                        errors.append(f"صفحة {page_no}: {inner}")
        index += len(chunk)

    if all(page is None or not page.text.strip() for page in parsed_by_page) and errors:
        raise UnlimitedOcrError("فشل OCR لجميع الصفحات: " + errors[0])

    pages: list[Page] = []
    for i, page in enumerate(parsed_by_page):
        if page is None:
            page = Page()
        page.error = next((e.split(": ", 1)[1] for e in errors if e.startswith(f"صفحة {i + 1}: ")), "")
        pages.append(page)
    return pages


def ocr_pdf(src_path: str, output_pdf: str, output_txt: str | None = None, *,
            cfg: dict | None = None, dpi: int | None = None,
            write_pdf: bool = True, cancel_check=None, progress=None) -> dict:
    """يعالج PDF كاملاً: TXT دائماً + PDF قابل للبحث إن أمكن."""
    cfg = cfg or load_config()
    pages = extract_pages(src_path, cfg, dpi=dpi,
                          cancel_check=cancel_check, progress=progress)
    text = pages_to_text(pages)
    if not text:
        raise UnlimitedOcrError("لا يوجد نص في نتيجة النموذج")

    if not output_txt:
        output_txt = os.path.splitext(src_path)[0] + "_OCR.txt"
    os.makedirs(os.path.dirname(os.path.abspath(output_txt)), exist_ok=True)
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(text)

    warnings: list[str] = []
    pdf_written = False
    for i, page in enumerate(pages):
        if page.error:
            warnings.append(f"صفحة {i + 1}: {page.error}")
    if write_pdf:
        if progress:
            progress("⏳ جارٍ بناء PDF قابل للبحث…")
        try:
            pdf_written = write_searchable_pdf(src_path, output_pdf, pages, cancel_check)
            if not pdf_written:
                warnings.append("reportlab غير مثبّت أو لا يوجد خط عربي — حُفظ النص فقط")
        except InterruptedError:
            raise
        except Exception as e:
            warnings.append(f"تعذّر بناء PDF قابل للبحث: {e}")

    return {
        "out_pdf": output_pdf if pdf_written else "",
        "out_txt": output_txt,
        "pages": len(pages),
        "chars": len(text),
        "pdf_written": pdf_written,
        "warnings": warnings,
        "pages_text": [p.text for p in pages],
    }


def extract_text(pdf_path: str, cfg: dict | None = None, *,
                 max_chars: int = 12000, cancel_check=None, progress=None) -> str:
    """نص المستند فقط — يستخدمه المساعد الذكي عند غياب طبقة النص."""
    pages = extract_pages(pdf_path, cfg, cancel_check=cancel_check, progress=progress)
    text = pages_to_text(pages)
    if max_chars and len(text) > max_chars:
        text = text[:max_chars]
    return text
