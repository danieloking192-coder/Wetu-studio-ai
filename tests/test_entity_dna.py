from wetu_studio.entity_dna import EntityDNA, EntityKind, EntitySource
from wetu_studio.scriptural_entity_catalog import build_scriptural_entity_catalog

def test_entity_dna_requires_provenance():
    e=EntityDNA("x","Dragon",EntityKind.DRAGON)
    assert "at least one provenance source is required" in e.validate()

def test_scriptural_catalog_has_multiple_sources():
    c=build_scriptural_entity_catalog()
    michael=c.get("angel-michael")
    assert len(michael.sources) >= 3
    assert c.get("demon-asmodai").kind is EntityKind.DEMON
    assert c.get("dragon-leviathan").kind is EntityKind.MYTHIC
