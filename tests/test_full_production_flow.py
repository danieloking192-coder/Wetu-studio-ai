from wetu_studio.creative_orchestrator import WetuCreativeOrchestrator
from wetu_studio.media_engine import MediaRegistry, LocalMediaProvider
from wetu_studio.models.production import CharacterDNA, WorldDNA, SceneMemory


def build_fixture():
    hero = CharacterDNA(
        character_id="hero",
        name="Amina",
        identity={"face":"stable","age_range":"adult"},
        appearance={"hair":"braided","eyes":"brown","clothing":"blue coat"},
        traits=["calm","determined"],
    )
    world = WorldDNA(
        world_id="kinshasa",
        name="Kinshasa",
        geography={"city":"Kinshasa"},
        architecture={"style":"contemporary"},
        environment={"weather":"warm"},
    )
    scenes = [
        SceneMemory(
            scene_id="s1", sequence=1, title="Arrival",
            summary="Amina arrives in the city.",
            character_ids=["hero"], world_id="kinshasa",
        ),
        SceneMemory(
            scene_id="s2", sequence=2, title="Decision",
            summary="Amina makes a difficult decision in the same world.",
            character_ids=["hero"], world_id="kinshasa",
        ),
    ]
    return hero, world, scenes


def test_full_production_flow_preserves_memory_and_continuity():
    registry = MediaRegistry()
    registry.register(LocalMediaProvider())
    orchestrator = WetuCreativeOrchestrator(media=registry)
    hero, world, scenes = build_fixture()

    result = orchestrator.produce(
        project_id="full-flow",
        brief="A realistic cinematic story about Amina.",
        characters=[hero],
        world=world,
        scenes=scenes,
        provider="local",
        kind="image",
        default_mood="tense",
    )

    assert result["pipeline"]["qa_before_generation"] is True
    assert result["pipeline"]["memory_preserved"] is True
    assert result["pipeline"]["visual_references_persisted"] is True
    assert result["pipeline"]["continuity_preflight"] is True

    generated = [x for x in result["assets"] if x["status"] == "generated"]
    assert len(generated) == 2

    reports = {x["scene_id"]: x for x in result["continuity"]}
    assert reports["s1"]["passed"] is True
    assert reports["s2"]["passed"] is True
    assert reports["s2"]["checked_references"] >= 2

    second_asset = next(x for x in generated if x["scene_id"] == "s2")
    metadata = second_asset["asset"]["metadata"]
    assert metadata["references"]
    assert any("s1" in uri for uri in metadata["references"])
