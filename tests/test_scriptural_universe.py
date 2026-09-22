from wetu_studio.scriptural_universe import *

def test_scriptural_universe_keeps_source_class():
    src=ScripturalSource("genesis","Genesis",SourceClass.CANONICAL,"biblical")
    u=ScripturalUniverse("u1","Genesis Cinematic",src,FidelityMode.SOURCE_FAITHFUL,
                         era="Ancient Near East",region="Levant",
                         provenance=["Genesis"])
    assert u.validate()==[]
    assert u.source.source_class is SourceClass.CANONICAL

def test_apocryphal_source_is_not_relabelled():
    src=ScripturalSource("tobit","Tobit",SourceClass.DEUTEROCANONICAL)
    u=ScripturalUniverse("u2","Tobit",src,FidelityMode.HISTORICAL_CINEMATIC,
                         era="Second Temple period",provenance=["Tobit"])
    assert u.source.source_class is SourceClass.DEUTEROCANONICAL

def test_realism_requires_historical_context():
    src=ScripturalSource("x","Example",SourceClass.APOCRYPHAL)
    u=ScripturalUniverse("u3","Example",src,FidelityMode.HISTORICAL_CINEMATIC,
                         provenance=["Example"])
    report=ScripturalRealismQA().evaluate(universe=u,scene_context={"source_passage":"1"})
    assert report.checks["historical_context"] is False
