import pytest
from wetu_studio.media_acceptance import MediaAcceptancePipeline, ProviderUrlPolicy, UnsafeProviderUrl

def test_provider_url_policy_requires_https_and_allowlist():
    policy=ProviderUrlPolicy({"fal.media"})
    with pytest.raises(UnsafeProviderUrl): policy.validate("http://fal.media/video.mp4")
    with pytest.raises(UnsafeProviderUrl): policy.validate("https://evil.example/video.mp4")

def test_provider_url_policy_rejects_private_resolution(monkeypatch):
    policy=ProviderUrlPolicy({"fal.media"})
    monkeypatch.setattr("wetu_studio.media_acceptance.socket.getaddrinfo",lambda *a,**k:[(2,1,6,"",("127.0.0.1",443))])
    with pytest.raises(UnsafeProviderUrl): policy.validate("https://fal.media/video.mp4")

def test_ffprobe_failure_rejects_media(monkeypatch):
    pipeline=MediaAcceptancePipeline(url_policy=ProviderUrlPolicy({"fal.media"}),max_bytes=1024)
    monkeypatch.setattr(pipeline,"_download",lambda url,destination: destination.write_bytes(b"broken") or 6)
    monkeypatch.setattr(pipeline.security,"scan",lambda path:type("R",(),{"clean":True,"sha256":"a"*64,"size_bytes":6,"engine":"test"})())
    monkeypatch.setattr(pipeline,"_ffprobe",lambda path: (_ for _ in ()).throw(ValueError("bad probe")))
    with pytest.raises(ValueError,match="bad probe"): pipeline.accept("https://fal.media/video.mp4")

def test_acceptance_report_shape(monkeypatch):
    pipeline=MediaAcceptancePipeline(url_policy=ProviderUrlPolicy({"fal.media"}),max_bytes=1024)
    monkeypatch.setattr(pipeline,"_download",lambda url,destination: destination.write_bytes(b"x") or 1)
    monkeypatch.setattr(pipeline.security,"scan",lambda path:type("R",(),{"clean":True,"sha256":"b"*64,"size_bytes":1,"engine":"test"})())
    monkeypatch.setattr(pipeline,"_ffprobe",lambda path:{"format":{"duration":"5.0"},"streams":[{"codec_type":"video","width":1280,"height":720,"avg_frame_rate":"30/1","codec_name":"h264"}]})
    monkeypatch.setattr(pipeline,"_decode_check",lambda path:None)
    path,report=pipeline.accept("https://fal.media/video.mp4")
    assert path.exists() and report.accepted and report.ffprobe["streams"][0]["codec_name"]=="h264"
    path.unlink()
