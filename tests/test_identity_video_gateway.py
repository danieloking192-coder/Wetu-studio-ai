import base64
from wetu_studio.character_identity import CharacterIdentityStore
from wetu_studio.identity_video_gateway import FalIdentityVideoGateway

class FakeFal:
    def __init__(self):
        self.uploads, self.calls = [], []
    def upload_file(self, path, lifecycle=None):
        self.uploads.append((path, lifecycle))
        return "https://fal.run/files/private-image"
    def subscribe(self, model, arguments):
        self.calls.append((model, arguments))
        return {"video": {"url": "https://fal.run/files/generated.mp4"}}

def test_gateway_uploads_identity_to_fal_and_generates_video(tmp_path):
    store = CharacterIdentityStore(tmp_path / "identity")
    item = store.import_image("hero", "portrait.jpg", "image/jpeg",
                              base64.b64encode(b"private-photo").decode(), True)
    fake = FakeFal()
    result = FalIdentityVideoGateway(model="test/model", api_key="secret", client=fake).generate(
        item, prompt="The person walks naturally.", duration=5, resolution="720p")
    assert result["real_media"] is True
    assert result["uri"].endswith(".mp4")
    assert fake.uploads[0][1] == "1h"
    assert fake.calls[0][1]["image_url"] == "https://fal.run/files/private-image"
    assert fake.calls[0][1]["prompt"] == "The person walks naturally."

def test_gateway_rejects_without_consent(tmp_path):
    store = CharacterIdentityStore(tmp_path / "identity")
    item = store.import_image("hero", "portrait.jpg", "image/jpeg",
                              base64.b64encode(b"photo").decode(), False, real_person=False)
    gateway = FalIdentityVideoGateway(model="test/model", api_key="secret", client=FakeFal())
    item.consent_confirmed = False
    try:
        gateway.generate(item, prompt="walk")
    except PermissionError:
        pass
    else:
        raise AssertionError("consent must be enforced")
