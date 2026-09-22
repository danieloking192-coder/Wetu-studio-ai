from wetu_studio.animation_engine import AnimationEngine, AnimationStyle, AnimationRequest
from wetu_studio.animation_qa import AnimationQA

def test_animation_styles_are_first_class():
    s=AnimationStyle("original-anime","anime","2D Japanese-inspired animation language","dynamic framing","expressive motion")
    req=AnimationRequest("a1","p","s",s,"hero enters the city")
    payload=AnimationEngine().build_request(req)
    assert payload["media"]=="animation"
    assert payload["style"]["medium"]=="anime"

def test_animation_qa_requires_output():
    s=AnimationStyle("toon","toon","stylized 2D")
    out=AnimationQA().evaluate(context={},style=s,result={})
    assert not out["passed"]
