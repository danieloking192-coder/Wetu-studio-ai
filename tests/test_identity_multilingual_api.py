import base64
from pathlib import Path
from wetu_studio.character_identity import CharacterIdentityStore, build_image_to_video_request
from wetu_studio.multilingual_production import MultilingualProductionRequest, build_language_pipeline

def test_identity_photo_contract(tmp_path):
    store=CharacterIdentityStore(tmp_path/"identity")
    item=store.import_image("hero-01","portrait.jpg","image/jpeg",base64.b64encode(b"photo").decode(),True)
    assert Path(item.path).exists()
    req=build_image_to_video_request(item,"Natural walking motion.")
    assert req["options"]["image_to_video"] is True

def test_tshiluba_output_contract():
    req=MultilingualProductionRequest("p1","s1","fr","tsh","Bonjour.")
    plan=build_language_pipeline(req)
    assert plan["ok"] is True
    assert plan["target_language"]=="tsh"
