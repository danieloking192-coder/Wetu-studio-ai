"""Curated scriptural narrative catalog for WETU.

This catalog stores metadata and narrative anchors, not copyrighted modern
translations. Canon status is represented by tradition rather than flattened.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from .scriptural_universe import SourceClass

@dataclass(frozen=True)
class NarrativeEntry:
    story_id: str
    title: str
    source_id: str
    source_class: SourceClass
    references: tuple[str, ...]
    characters: tuple[str, ...]
    places: tuple[str, ...]
    era: str
    themes: tuple[str, ...]
    realism_notes: tuple[str, ...] = ()

CATALOG: tuple[NarrativeEntry, ...] = (
    NarrativeEntry("creation","Creation","genesis","canonical",("Genesis 1-2",),("God","Adam","Eve"),("Eden",),"primeval","creation"),
    NarrativeEntry("flood","Noah and the Flood","genesis","canonical",("Genesis 6-9",),("Noah",),("Ark","Ararat"),"primeval","judgment;covenant"),
    NarrativeEntry("abraham","Abraham's Call","genesis","canonical",("Genesis 12",),("Abraham","Sarah"),("Ur","Canaan"),"Bronze Age","covenant;journey"),
    NarrativeEntry("exodus","The Exodus","exodus","canonical",("Exodus 1-15",),("Moses","Aaron","Pharaoh"),("Egypt","Red Sea","Sinai"),"Late Bronze Age","liberation;covenant"),
    NarrativeEntry("jericho","Jericho","joshua","canonical",("Joshua 6",),("Joshua",),("Jericho",),"Iron Age transition","conquest;faith"),
    NarrativeEntry("david_goliath","David and Goliath","1samuel","canonical",("1 Samuel 17",),("David","Goliath","Saul"),("Valley of Elah",),"Iron Age","courage;kingship"),
    NarrativeEntry("solomon","Solomon's Temple","1kings","canonical",("1 Kings 5-8",),("Solomon",),("Jerusalem",),"Iron Age","temple;kingship"),
    NarrativeEntry("jonah","Jonah","jonah","canonical",("Jonah 1-4",),("Jonah",),("Joppa","Nineveh"),"Iron Age","prophecy;mercy"),
    NarrativeEntry("daniel_fire","The Fiery Furnace","daniel","canonical",("Daniel 3",),("Daniel","Shadrach","Meshach","Abednego"),("Babylon",),"6th century BCE","faith;deliverance"),
    NarrativeEntry("daniel_lions","Daniel in the Lions' Den","daniel","canonical",("Daniel 6",),("Daniel","Darius"),("Babylon",),"6th century BCE","faith;deliverance"),
    NarrativeEntry("esther","Esther","esther","canonical",("Esther 1-10",),("Esther","Mordecai","Ahasuerus"),("Susa",),"Persian period","courage;deliverance"),
    NarrativeEntry("job","Job","job","canonical",("Job 1-42",),("Job",),("Uz",),"ancient setting","suffering;wisdom"),
    NarrativeEntry("nativity","Birth of Jesus","matthew_luke","canonical",("Matthew 1-2","Luke 1-2"),("Jesus","Mary","Joseph"),("Bethlehem","Nazareth","Jerusalem"),"1st century BCE/CE","incarnation;messiah"),
    NarrativeEntry("baptism","Baptism of Jesus","matthew_mark_luke_john","canonical",("Matthew 3","Mark 1","Luke 3"),("Jesus","John the Baptist"),("Jordan",),"1st century CE","baptism;messiah"),
    NarrativeEntry("crucifixion","Crucifixion","gospels","canonical",("Matthew 27","Mark 15","Luke 23","John 19"),("Jesus","Pilate"),("Jerusalem","Golgotha"),"1st century CE","passion;resurrection"),
    NarrativeEntry("resurrection","Resurrection","gospels","canonical",("Matthew 28","Mark 16","Luke 24","John 20"),("Jesus","Mary Magdalene"),("Jerusalem","Tomb"),"1st century CE","resurrection;faith"),
    NarrativeEntry("tobit","Tobit and Tobias","tobit","deuterocanonical",("Tobit 1-14",),("Tobit","Tobias","Sarah","Raphael"),("Nineveh","Media","Ecbatana"),"Second Temple period","family;healing;providence"),
    NarrativeEntry("judith","Judith and Holofernes","judith","deuterocanonical",("Judith 8-16",),("Judith","Holofernes"),("Bethulia","Assyrian camp"),"Second Temple period","courage;deliverance"),
    NarrativeEntry("maccabees","Maccabean Revolt","1maccabees_2maccabees","deuterocanonical",("1 Maccabees 1-16","2 Maccabees 1-15"),("Mattathias","Judas Maccabeus"),("Judea","Jerusalem"),"2nd century BCE","resistance;religious freedom"),
    NarrativeEntry("susanna","Susanna","daniel_additions","deuterocanonical",("Daniel 13",),("Susanna","Daniel"),("Babylon",),"ancient setting","justice;wisdom"),
    NarrativeEntry("bel_dragon","Bel and the Dragon","daniel_additions","deuterocanonical",("Daniel 14",),("Daniel",),("Babylon",),"ancient setting","idolatry;wisdom"),
    NarrativeEntry("enoch_watchers","The Watchers and Enoch","1_enoch","pseudepigraphal",("1 Enoch 1-36",),("Enoch","Watchers","angels"),("heavenly realms","earth"),"Second Temple period","watchers;judgment;cosmic order"),
    NarrativeEntry("enoch_heavenly_journeys","Enoch's Heavenly Journeys","1_enoch","pseudepigraphal",("1 Enoch 17-36",),("Enoch","angels"),("heavenly realms","cosmic regions"),"Second Temple period","visions;cosmology;judgment"),
    NarrativeEntry("enoch_parables","The Parables of Enoch","1_enoch","pseudepigraphal",("1 Enoch 37-71",),("Enoch","Son of Man","angels"),("heavenly realms"),"Second Temple period","judgment;eschatology"),
    NarrativeEntry("enoch_astronomical","The Astronomical Book","1_enoch","pseudepigraphal",("1 Enoch 72-82",),("Enoch","Uriel"),("cosmic realms"),"Second Temple period","calendar;luminaries;cosmology"),
    NarrativeEntry("enoch_dreams","The Book of Dreams","1_enoch","pseudepigraphal",("1 Enoch 83-90",),("Enoch","Noah"),("earth","visionary realms"),"Second Temple period","visions;judgment;history"),
    NarrativeEntry("enoch_epistle","The Epistle of Enoch","1_enoch","pseudepigraphal",("1 Enoch 91-108",),("Enoch","righteous","sinners"),("earth","heavenly realms"),"Second Temple period","wisdom;judgment;eschatology"),
)

def get_story(story_id: str) -> NarrativeEntry:
    for item in CATALOG:
        if item.story_id == story_id:
            return item
    raise KeyError(story_id)

def catalog_summary() -> dict[str, Any]:
    counts={}
    for item in CATALOG:
        counts[item.source_class.value]=counts.get(item.source_class.value,0)+1
    return {"stories":len(CATALOG),"by_source_class":counts}

def story_manifest(story_id: str) -> dict[str, Any]:
    return asdict(get_story(story_id))
