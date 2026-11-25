"""
مساعد مستندات محلي — يلخّص ويجيب عن أسئلة حول محتوى PDF.
المسار الافتراضي: Ollama محلياً. اختياري: واجهة OpenAI-compatible عبر مفتاح API.
"""

import json
import os
import urllib.error
import urllib.request


class AiError(Exception):
    pass


def extract_document_text(
    path: str,
    max_chars: int = 12000,
    *,
    ocr_fallback: bool = False,
    ocr_config: dict | None = None,
    cancel_check=None,
    progress=None,
) -> str:
    """يستخرج نص PDF مع قصّه لحد أقصى مناسب للنماذج الخفيفة.

    إن كانت الصفحات ممسوحة (بلا طبقة نص) و``ocr_fallback`` مفعّلاً،
    يُستخرج النص عبر Unlimited-OCR ثم يُعاد استخدامه كالمعتاد.
    """
    try:
        import fitz
    except ImportError as e:
        raise AiError("PyMuPDF غير مثبّت") from e
    if not os.path.isfile(path):
        raise FileNotFoundError(f"الملف غير موجود: {path}")
    doc = fitz.open(path)
    try:
        chunks = []
        total = 0
        pages_with_text = 0
        page_count = len(doc)
        for i, page in enumerate(doc):
            t = (page.get_text("text") or "").strip()
            if not t:
                continue
            pages_with_text += 1
            header = f"\n--- صفحة {i + 1} ---\n"
            piece = header + t
            if total + len(piece) > max_chars:
                remain = max_chars - total
                if remain > 100:
                    chunks.append(piece[:remain])
                break
            chunks.append(piece)
            total += len(piece)
        text = "".join(chunks).strip()
    finally:
        doc.close()

    # مستند ممسوح أو شبه فارغ: جرّب Unlimited-OCR إن كان مفعّلاً
    sparse = page_count > 0 and (len(text) < 40 or pages_with_text < page_count * 0.5)
    if sparse and ocr_fallback:
        from core import unlimited_ocr
        if cancel_check and cancel_check():
            raise InterruptedError("تم إلغاء العملية")
        try:
            ocr_text = unlimited_ocr.extract_text(
                path, ocr_config, max_chars=max_chars,
                cancel_check=cancel_check, progress=progress)
        except InterruptedError:
            raise
        except Exception as e:
            if text:
                return text
            raise AiError(str(e)) from e
        if ocr_text.strip():
            return ocr_text
        if text:
            return text

    if not text:
        raise AiError(
            "لا يوجد نص قابل للاستخراج في الملف.\n"
            "جرّب أولاً أداة OCR للمستندات الممسوحة."
        )
    return text


def ollama_available(base_url: str = "http://127.0.0.1:11434") -> bool:
    try:
        req = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def list_ollama_models(base_url: str = "http://127.0.0.1:11434") -> list[str]:
    try:
        req = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m.get("name") for m in data.get("models", []) if m.get("name")]
    except Exception:
        return []


def _chat_ollama(messages: list[dict], model: str, base_url: str) -> str:
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return (data.get("message") or {}).get("content") or ""
    except urllib.error.URLError as e:
        raise AiError(f"تعذّر الاتصال بـ Ollama: {e}") from e


def _chat_openai_compatible(
    messages: list[dict],
    model: str,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
) -> str:
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.3,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise AiError(f"خطأ API ({e.code}): {body[:300]}") from e
    except Exception as e:
        raise AiError(f"فشل طلب API: {e}") from e


def ask_about_document(
    pdf_path: str,
    question: str,
    *,
    mode: str = "ollama",
    model: str = "llama3.2",
    api_key: str = "",
    api_base: str = "https://api.openai.com/v1",
    ollama_base: str = "http://127.0.0.1:11434",
    lang: str = "ar",
    ocr_fallback: bool = False,
    ocr_config: dict | None = None,
    cancel_check=None,
    progress=None,
) -> str:
    """
    يسأل عن محتوى المستند.
    mode: 'ollama' | 'api'
    lang: لغة الإجابة المطلوبة ('ar' | 'en')
    """
    english = lang == "en"
    if cancel_check and cancel_check():
        raise AiError("Operation cancelled" if english else "تم إلغاء العملية")
    text = extract_document_text(
        pdf_path,
        ocr_fallback=ocr_fallback,
        ocr_config=ocr_config,
        cancel_check=cancel_check,
        progress=progress,
    )
    if english:
        system = (
            "You are a privacy-preserving local document assistant. "
            "Answer in English briefly and clearly, based only on the attached document text. "
            "If the information is not in the text, say so explicitly."
        )
        user = f"Document text:\n{text}\n\nUser question:\n{question}"
    else:
        system = (
            "أنت مساعد مستندات يعمل محلياً ويحافظ على الخصوصية. "
            "أجب بالعربية باختصار ووضوح اعتماداً فقط على نص المستند المرفق. "
            "إن لم تجد المعلومة في النص فقل ذلك صراحة."
        )
        user = f"نص المستند:\n{text}\n\nسؤال المستخدم:\n{question}"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    if mode == "api":
        if not api_key.strip():
            raise AiError("Enter an API key first" if english else "أدخل مفتاح API أولاً")
        return _chat_openai_compatible(messages, model=model or "gpt-4o-mini", api_key=api_key, base_url=api_base)
    if not ollama_available(ollama_base):
        raise AiError(
            "Ollama is not available locally.\n"
            "Install it from https://ollama.com and run a model such as: ollama run llama3.2\n"
            "Or use the optional cloud API mode."
            if english else
            "Ollama غير متاح محلياً.\n"
            "ثبّته من https://ollama.com وشغّل نموذجاً مثل: ollama run llama3.2\n"
            "أو استخدم وضع API السحابي الاختياري."
        )
    return _chat_ollama(messages, model=model or "llama3.2", base_url=ollama_base)


def summarize_document(
    pdf_path: str,
    *,
    mode: str = "ollama",
    model: str = "llama3.2",
    api_key: str = "",
    api_base: str = "https://api.openai.com/v1",
    ollama_base: str = "http://127.0.0.1:11434",
    lang: str = "ar",
    ocr_fallback: bool = False,
    ocr_config: dict | None = None,
    cancel_check=None,
    progress=None,
) -> str:
    question = (
        "Summarize this document in clear bullet points and mention the key clauses if present (contracts/reports)."
        if lang == "en" else
        "لخّص هذا المستند في نقاط واضحة، واذكر أهم البنود إن وُجدت (عقود/تقارير)."
    )
    return ask_about_document(
        pdf_path,
        question,
        mode=mode,
        model=model,
        api_key=api_key,
        api_base=api_base,
        ollama_base=ollama_base,
        lang=lang,
        ocr_fallback=ocr_fallback,
        ocr_config=ocr_config,
        cancel_check=cancel_check,
        progress=progress,
    )
