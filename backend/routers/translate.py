"""Auto-translation route."""
from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user
from core.models import TranslateIn
from core.translation import translate_text

router = APIRouter()


@router.post("")
async def translate(body: TranslateIn, current=Depends(get_current_user)):
    if not body.text or not body.target_language:
        raise HTTPException(400, "Missing text or target_language")

    translated, provider, note = translate_text(
        body.text.strip(),
        body.target_language,
        body.source_language,
    )
    out = {"translated": translated, "target_language": body.target_language.lower(), "provider": provider}
    if note:
        out["note"] = note
    return out