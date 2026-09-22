import json
from unittest.mock import patch
from wetu_studio.media_engine import HttpMediaProvider, MediaRequest

class Response:
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def read(self): return json.dumps({"model":"remote-v1","uri":"https://media.example/a.png","real_media":True}).encode()

def test_http_provider_uses_wetu_contract():
    p=HttpMediaProvider("remote","https://provider.example/generate","secret")
    req=MediaRequest("r1","p","s","image","hello","remote")
    with patch("wetu_studio.media_engine.urlopen", return_value=Response()):
        out=p.generate(req, {"scene":"context"})
    assert out["real_media"] is True
    assert out["uri"].startswith("https://")
