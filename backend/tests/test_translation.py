"""Unit tests for translation chunking (no network)."""
from core.translation import MYMEMORY_MAX_CHARS, chunk_text, is_bad_translation, translate_text


def test_chunk_text_short_unchanged():
    text = "Hello world"
    assert chunk_text(text) == [text]


def test_chunk_text_long_reassembles():
    text = "A" * 1200
    chunks = chunk_text(text, max_len=400)
    assert len(chunks) == 3
    assert "".join(chunks) == text
    assert all(len(c) <= 400 for c in chunks)


def test_chunk_text_prefers_sentence_boundary():
    sentence = "This is one sentence. " * 30
    chunks = chunk_text(sentence, max_len=200)
    assert "".join(chunks) == sentence
    assert len(chunks) > 1
    for chunk in chunks[:-1]:
        assert chunk.endswith((". ", "! ", "? ", "\n", "\n\n")) or len(chunk) == 200


def test_chunk_text_preserves_newlines():
    text = "Line one.\n\nLine two is longer and continues here.\n\n" + ("word " * 200)
    chunks = chunk_text(text, max_len=300)
    assert "".join(chunks) == text


def test_is_bad_translation_filters_mymemory_errors():
    assert is_bad_translation("PLEASE SELECT TWO DISTINCT LANGUAGES")
    assert is_bad_translation("MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS")
    assert not is_bad_translation("Hello, how are you?")


def test_translate_text_same_language_short_circuits():
    out, provider, note = translate_text("Hola", "es", "es")
    assert out == "Hola"
    assert provider == "none"
    assert note == "same language"