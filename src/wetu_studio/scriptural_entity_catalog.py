"""Multi-source catalog for scriptural/symbolic beings.

The catalog stores provenance separately from cinematic interpretation. It does
not claim that traditions agree with one another; each source remains traceable.
"""
from __future__ import annotations
from .entity_dna import EntityCatalog, EntityDNA, EntityKind, EntitySource

def build_scriptural_entity_catalog() -> EntityCatalog:
    c=EntityCatalog()
    entries=[
      EntityDNA("angel-michael","Michael",EntityKind.ANGEL,
        identity={"role":"archangel / heavenly figure"},
        abilities=["source-described authority or combat role"],
        sources=[
          EntitySource("daniel-10","Daniel 10","Hebrew Bible","Daniel 10","named heavenly prince"),
          EntitySource("daniel-12","Daniel 12","Hebrew Bible","Daniel 12","associated with the people"),
          EntitySource("jude-9","Jude 9","New Testament","Jude 9","Michael is named as archangel"),
          EntitySource("revelation-12","Revelation 12","New Testament","Revelation 12","Michael leads heavenly forces in the vision"),
        ],
        interpretation_notes=["Render each source descriptor separately; do not silently merge later tradition into the biblical text."]),
      EntityDNA("angel-gabriel","Gabriel",EntityKind.ANGEL,
        identity={"role":"messenger figure"},
        sources=[
          EntitySource("daniel-8-9","Daniel 8-9","Hebrew Bible","Daniel 8-9","named messenger/interpreter"),
          EntitySource("luke-1","Luke 1","New Testament","Luke 1","named messenger in the annunciation narratives"),
        ]),
      EntityDNA("angel-raphael","Raphael",EntityKind.ANGEL,
        identity={"role":"healing/guide figure in Tobit tradition"},
        sources=[EntitySource("tobit","Tobit","Deuterocanonical","Tobit 3-12","named angel and companion/guide")]),
      EntityDNA("angel-uriel","Uriel",EntityKind.ANGEL,
        identity={"role":"angelic figure in selected later texts/traditions"},
        sources=[
          EntitySource("1-enoch","1 Enoch","Pseudepigraphal","1 Enoch","Uriel is named among heavenly beings"),
          EntitySource("4-ezra","4 Ezra","Apocryphal","4 Ezra","Uriel appears as an angelic interlocutor"),
        ],
        interpretation_notes=["Tradition/source classification can vary by canon and scholarly convention."]),
      EntityDNA("demon-asmodai","Asmodeus",EntityKind.DEMON,
        identity={"role":"adversarial/demonic figure"},
        sources=[EntitySource("tobit","Tobit","Deuterocanonical","Tobit 3, 6, 8","Asmodeus is the named adversary in Tobit")]),
      EntityDNA("satan-adversary","Satan / the adversary",EntityKind.DEMON,
        identity={"role":"adversarial figure; terminology varies by text and tradition"},
        sources=[
          EntitySource("job-1-2","Job 1-2","Hebrew Bible","Job 1-2","the satan appears as an accuser/adversarial figure"),
          EntitySource("zechariah-3","Zechariah 3","Hebrew Bible","Zechariah 3","the satan appears as an accuser"),
          EntitySource("matthew-4","Matthew 4","New Testament","Matthew 4","the tempter is identified as the devil"),
          EntitySource("revelation-12","Revelation 12","New Testament","Revelation 12","the dragon is identified with the devil/Satan"),
        ],
        interpretation_notes=["WETU must preserve the terminology and context of each source instead of treating every later theological identification as identical."]),
      EntityDNA("demon-belial","Belial",EntityKind.DEMON,
        identity={"role":"name/title with varying textual and later traditional uses"},
        sources=[
          EntitySource("2-corinthians-6","2 Corinthians 6","New Testament","2 Corinthians 6","Belial is contrasted with Christ"),
          EntitySource("dead-sea-scrolls","Dead Sea Scrolls","Second Temple Jewish literature","selected texts","Belial appears in adversarial contexts"),
        ],
        interpretation_notes=["Exact ontology and visual form should be source-specific; do not invent a canonical body where the source does not describe one."]),
      EntityDNA("dragon-leviathan","Leviathan",EntityKind.MYTHIC,
        identity={"role":"sea/chaotic creature in biblical poetry and later interpretation"},
        morphology={"source_described":"aquatic/serpentine imagery varies by passage"},
        sources=[
          EntitySource("job-41","Job 41","Hebrew Bible","Job 41","extended creature description"),
          EntitySource("psalm-74","Psalm 74","Hebrew Bible","Psalm 74","Leviathan in poetic imagery"),
          EntitySource("isaiah-27","Isaiah 27","Hebrew Bible","Isaiah 27","Leviathan as a fleeing/serpent-like creature"),
        ],
        interpretation_notes=["Visual reconstruction must distinguish textual description from later artistic tradition."]),
    ]
    for e in entries: c.add(e)
    return c

CATALOG=build_scriptural_entity_catalog()
