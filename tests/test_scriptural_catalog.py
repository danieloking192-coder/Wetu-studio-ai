from wetu_studio.scriptural_catalog import catalog_summary, get_story
from wetu_studio.scriptural_universe import SourceClass

def test_catalog_has_canonical_and_deuterocanonical_narratives():
    s=catalog_summary()
    assert s["stories"] >= 20
    assert s["by_source_class"]["canonical"] > 0
    assert s["by_source_class"]["deuterocanonical"] > 0

def test_story_keeps_source_reference_and_realism_context():
    x=get_story("exodus")
    assert x.source_class is SourceClass.CANONICAL
    assert "Exodus 1-15" in x.references
    assert "Egypt" in x.places

def test_tobit_is_marked_deuterocanonical():
    assert get_story("tobit").source_class is SourceClass.DEUTEROCANONICAL
