"""Translation providers: MyMemory (free) and optional Google Cloud Translate."""
import os
from typing import Optional, Tuple

import requests

from core.logging_config import logger

PROVIDER = (os.environ.get("TRANSLATION_PROVIDER") or "mymemory").lower().strip()
GOOGLE_API_KEY = (os.environ.get("GOOGLE_TRANSLATE_API_KEY") or "").strip()


def _mymemory(text: str, target: str, source: Optional[str]) -> Optional[str]:
    src = (source or "autodetect").lower().strip()
    try:
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text[:500], "langpair": f"{src}|{target}"},
            timeout=8,
        )
        if r.status_code == 200:
            body = r.json()
            translated = body.get("responseData", {}).get("translatedText")
            if translated:
                # MyMemory returns quota warnings inside translatedText on failure
                if "MYMEMORY WARNING" in translated.upper():
                    logger.warning(f"MyMemory quota/limit: {translated[:120]}")
                    return None
                if translated.lower() != text.lower():
                    return translated
    except Exception as e:
        logger.warning(f"MyMemory translate failed: {e}")
    return None


def _google(text: str, target: str, source: Optional[str]) -> Optional[str]:
    if not GOOGLE_API_KEY:
        logger.warning("TRANSLATION_PROVIDER=google but GOOGLE_TRANSLATE_API_KEY unset")
        return None
    try:
        r = requests.post(
            "https://translation.googleapis.com/language/translate/v2",
            params={"key": GOOGLE_API_KEY},
            json={
                "q": text[:5000],
                "target": target,
                "source": source or None,
                "format": "text",
            },
            timeout=10,
        )
        if r.status_code == 200:
            items = r.json().get("data", {}).get("translations", [])
            if items:
                translated = items[0].get("translatedText", "")
                if translated and translated.lower() != text.lower():
                    return translated
        else:
            logger.warning(f"Google translate HTTP {r.status_code}")
    except Exception as e:
        logger.warning(f"Google translate failed: {e}")
    return None


def translate_text(text: str, target_language: str, source_language: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    """
    Returns (translated_text, provider_used, note).
    Falls back through configured provider → MyMemory → original text.
    """
    target = target_language.lower().strip()
    if not text or not target:
        return text, "none", "missing text or target"
    if source_language and source_language.lower().strip() == target:
        return text, "none", "same language"

    providers = []
    if PROVIDER == "google":
        providers = ["google", "mymemory"]
    elif PROVIDER == "none":
        return text, "none", "translation disabled by provider"
    else:
        providers = ["mymemory"]

    tried = []
    for name in providers:
        fn = _google if name == "google" else _mymemory
        result = fn(text, target, source_language)
        tried.append(name)
        if result:
            return result, name, None
        # Retry MyMemory with autodetect if a wrong source was supplied
        if name == "mymemory" and source_language and source_language.lower() != "autodetect":
            result = fn(text, target, None)
            if result:
                return result, name, None

    return text, tried[-1] if tried else PROVIDER, "translation service unavailable or same language"