"""Engine 9 — M5 closure and translation mode policy."""
import os
from unittest.mock import patch

from core.metadata_policy import METADATA_GAPS
from core.translation_policy import (
    TranslationMode,
    m5_closed,
    production_translation_mode,
)


def test_m5_marked_resolved_in_metadata_policy():
    m5 = next(g for g in METADATA_GAPS if g.gap_id == "M5")
    assert m5.resolved is True
    assert m5.later_engine == "9"


def test_m5_closed_when_server_disabled():
    with patch.dict(os.environ, {"TRANSLATION_ENABLED": "false"}, clear=False):
        assert m5_closed() is True


def test_m5_open_when_server_explicitly_enabled():
    with patch.dict(
        os.environ,
        {"TRANSLATION_ENABLED": "true", "TRANSLATION_PROVIDER": "mymemory"},
        clear=False,
    ):
        assert m5_closed() is False


def test_production_mode_on_device_by_default():
    with patch.dict(os.environ, {"TRANSLATION_ENABLED": "false"}, clear=False):
        assert production_translation_mode() == TranslationMode.ON_DEVICE