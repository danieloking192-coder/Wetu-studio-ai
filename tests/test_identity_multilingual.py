from pathlib import Path
import base64
from wetu_studio.character_identity import CharacterIdentityStore, build_image_to_video_request
from wetu_studio.multilingual_production import MultilingualProductionRequest, build_language_pipeline

def test_photo_becomes_persistent_character_reference(tmp_path):
    store=CharacterIdentityStore(tmp_path/"identity")
    item=store.import_image("hero-01","portrait.jpg","image/jpeg",base64.b64encode(b"\xff\xd8\xff\xe0" + b"fake-image").decode(),True)
    assert item.sha256 and Path(item.path).exists()
    request=build_image_to_video_request(item,"The person walks naturally toward camera.")
    assert request["options"]["image_to_video"] is True and request["options"]["preserve_identity"] is True

def test_real_person_requires_consent(tmp_path):
    store=CharacterIdentityStore(tmp_path/"identity")
    try: store.import_image("hero-01","portrait.jpg","image/jpeg",base64.b64encode(b"\xff\xd8\xff\xe0x").decode(),False)
    except PermissionError: pass
    else: raise AssertionError("real-person import must require consent")

def test_french_to_tshiluba_pipeline():
    req=MultilingualProductionRequest("p1","scene-1","fr","tsh","Bonjour, nous devons partir maintenant.")
    pipeline=build_language_pipeline(req)
    assert pipeline["ok"] is True and pipeline["target_language"]=="tsh" and "lip_sync" in pipeline["stages"]
