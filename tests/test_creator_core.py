from wetu_studio.creator_core import CreatorApplicationCore, CreatorState
from wetu_studio.models.production import CharacterDNA, SceneMemory, WorldDNA

class FakeProvider:
    name = "fake"
    def generate(self, *, kind, prompt, context):
        return {"model": "fake-v1", "asset_url": "memory://asset", "kind": kind}

class PassQA:
    def evaluate(self, *, kind, context, result):
        return {"passed": True, "checks": ["provider_result_present"]}

def test_creator_core_preserves_dna_and_memory():
    state = CreatorState(project_id="p1")
    core = CreatorApplicationCore(state, providers={"fake": FakeProvider()}, qa=PassQA())
    core.add_character(CharacterDNA(character_id="c1", name="Amina", wardrobe={"dress": "blue"}))
    core.add_world(WorldDNA(world_id="w1", name="Kinshasa", architecture={"style": "urban"}))
    core.add_scene(SceneMemory(scene_id="s1", project_id="p1", sequence=1,
                               character_ids=["c1"], world_id="w1"))
    result = core.generate(scene_id="s1", provider="fake", kind="image",
                           prompt="A cinematic street scene", generation_id="g1")
    assert result["status"] == "qa_passed"
    assert state.characters["c1"].name == "Amina"
    assert state.worlds["w1"].name == "Kinshasa"
    assert state.memory.generations["g1"].provider == "fake"
