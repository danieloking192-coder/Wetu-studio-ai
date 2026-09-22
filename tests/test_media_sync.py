from wetu_studio.media_sync import MediaSyncEngine, SyncCue

def test_media_sync_manifest_keeps_voice_and_subtitle_timing():
    cues=[SyncCue("l1",0,1200,"hero","ln","Mbote","voice-1"),
          SyncCue("l2",1200,2500,"hero","fr","Bonjour","voice-2")]
    manifest=MediaSyncEngine().build_manifest(cues)
    assert manifest[0]["voice_request_id"] == "voice-1"
    assert manifest[0]["start_ms"] == 0 and manifest[1]["start_ms"] == 1200

def test_media_sync_rejects_overlap_and_invalid_timing():
    engine=MediaSyncEngine()
    try:
        engine.build_manifest([SyncCue("a",0,1000,"h","fr","A"),SyncCue("b",900,1200,"h","fr","B")])
        assert False
    except ValueError as exc:
        assert "overlap" in str(exc)


def test_media_sync_manifest_persists_in_production_memory():
    from wetu_studio.models.production import ProductionMemory
    memory = ProductionMemory()
    manifest = MediaSyncEngine().build_manifest([SyncCue("l1", 0, 1200, "hero", "ln", "Mbote", "voice-1")])
    memory.add_sync_manifest("sync-1", manifest)
    assert memory.sync_manifests["sync-1"][0]["voice_request_id"] == "voice-1"
