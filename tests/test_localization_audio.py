import json
from unittest.mock import patch

import pytest

from wetu_studio.audio_pipeline import HttpAudioProvider, VoiceRequest
from wetu_studio.multilingual_production import HttpTranslationProvider, MultilingualProductionRequest, build_language_pipeline


def test_tshiluba_language_pipeline_is_supported():
    req = MultilingualProductionRequest("p1", "s1", "fr", "tsh", "Bonjour, bienvenue à Kinshasa.")
    plan = build_language_pipeline(req)
    assert plan["ok"] is True
    assert plan["target_language"] == "tsh"
    assert "meaning_preserving_translation" in plan["stages"]


def test_translation_provider_requires_https():
    with pytest.raises(ValueError):
        HttpTranslationProvider("http://example.invalid")


def test_translation_provider_rejects_empty_response():
    provider = HttpTranslationProvider("https://translation.invalid")
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps({"text": ""}).encode()
    with patch("wetu_studio.multilingual_production.urlopen", return_value=Response()):
        with pytest.raises(ValueError):
            provider.translate(source_language="fr", target_language="tsh", script="Bonjour")


def test_audio_provider_requires_https():
    with pytest.raises(ValueError):
        HttpAudioProvider("http://example.invalid")


def test_audio_provider_accepts_contract_response():
    provider = HttpAudioProvider("https://audio.invalid")
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps({"uri": "https://cdn.invalid/audio.wav"}).encode()
    request = VoiceRequest("v1", "p1", "s1", "amina", "tsh", "Muakane!")
    with patch("wetu_studio.audio_pipeline.urlopen", return_value=Response()):
        result = provider.generate(request, {})
    assert result["real_audio"] is True
    assert result["uri"].startswith("https://")
