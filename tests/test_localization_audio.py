from wetu_studio.localization_engine import LocalizationEngine, LocalizationTrack
from wetu_studio.audio_pipeline import AudioRegistry, VoiceRequest

def test_multilingual_lines_and_subtitles():
    t=LocalizationTrack("scene-1")
    e=LocalizationEngine()
    e.add_line(t,"l1","hero","fr","Bonjour","voice-fr")
    e.add_line(t,"l2","hero","ln","Mbote","voice-ln")
    assert e.languages(t)==["fr","ln"]
    assert len(e.export_subtitles(t))==2

def test_audio_provider_is_explicitly_non_real():
    r=AudioRegistry()
    x=r.generate(VoiceRequest("a1","p","s","hero","fr","Bonjour"))
    assert x["status"]=="READY" and x["real_audio"] is False