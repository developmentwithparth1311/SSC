"""Upload validation — allowed MIME types and magic-byte sniffing."""
from typing import Optional, Tuple

# (mime_prefix_or_exact, magic_bytes_at_start)
_SIGNATURES: Tuple[Tuple[str, bytes], ...] = (
    ("image/jpeg", b"\xff\xd8\xff"),
    ("image/png", b"\x89PNG\r\n\x1a\n"),
    ("image/gif", b"GIF87a"),
    ("image/gif", b"GIF89a"),
    ("image/webp", b"RIFF"),  # RIFF....WEBP checked below
    ("application/pdf", b"%PDF"),
    ("audio/ogg", b"OggS"),
    ("audio/mpeg", b"\xff\xfb"),
    ("audio/mpeg", b"ID3"),
    ("audio/wav", b"RIFF"),  # RIFF....WAVE checked below
    ("video/webm", b"\x1a\x45\xdf\xa3"),
)

ALLOWED_CONTENT_TYPES = frozenset({
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf", "text/plain",
    "audio/ogg", "audio/mpeg", "audio/mp3", "audio/wav", "audio/webm", "audio/mp4",
    "video/mp4", "video/webm", "video/quicktime",
    "application/octet-stream",  # voice blobs from browser recorder
})


def _match_webp(data: bytes) -> bool:
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"


def _match_wav(data: bytes) -> bool:
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE"


def sniff_content_type(data: bytes, declared: Optional[str]) -> Optional[str]:
    """Return normalized content type if data matches a known signature."""
    if not data:
        return None
    if _match_webp(data):
        return "image/webp"
    if _match_wav(data):
        return "audio/wav"
    for mime, magic in _SIGNATURES:
        if mime == "image/webp" or mime == "audio/wav":
            continue
        if data.startswith(magic):
            return mime
    if declared and declared.split(";")[0].strip().lower() in ALLOWED_CONTENT_TYPES:
        # Plain text / small voice payloads without strong magic
        if declared.startswith("text/") or declared == "application/octet-stream":
            return declared.split(";")[0].strip().lower()
    return None


def validate_upload(data: bytes, declared_type: Optional[str]) -> Tuple[bool, str, str]:
    """
    Returns (ok, error_message, normalized_content_type).
    """
    declared = (declared_type or "application/octet-stream").split(";")[0].strip().lower()
    if declared == "text/plain" and data:
        return True, "", declared
    if declared not in ALLOWED_CONTENT_TYPES:
        return False, f"File type not allowed: {declared}", declared

    sniffed = sniff_content_type(data, declared)
    if sniffed and sniffed != declared and declared != "application/octet-stream":
        # Declared must match sniffed for typed uploads (except generic octet-stream)
        if not (declared.startswith("audio/") and sniffed.startswith("audio/")):
            if not (declared.startswith("video/") and sniffed.startswith("video/")):
                return False, "File content does not match declared type", declared

    if declared == "application/octet-stream" and len(data) > 512:
        # Large opaque blobs must match a known signature
        if not sniffed and not data[:32].strip():  # allow tiny voice chunks
            pass
        elif not sniffed and len(data) > 4096:
            return False, "Unrecognized file format", declared

    normalized = sniffed or declared
    return True, "", normalized