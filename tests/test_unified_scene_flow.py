"""End-to-end contract smoke tests for the unified WETU scene flow."""
import unittest

from wetu_studio.creator_core import CreatorApplicationCore, CreatorState
from wetu_studio.models.production import CharacterDNA, SceneMemory, WorldDNA
from wetu_studio.production_realism import ProductionRealismOrchestrator


class UnifiedSceneFlowTests(unittest.TestCase):
    def test_full_scene_contract(self):
        state = CreatorState(project_id="demo")
        core = CreatorApplicationCore(state)
        core.add_character(CharacterDNA(character_id="hero", name="Amina"))
        core.add_world(WorldDNA(world_id="world", name="Kinshasa"))
        core.add_scene(SceneMemory(
            scene_id="s1",
            project_id="demo",
            sequence=1,
            character_ids=["hero"],
            world_id="world",
        ))
        ctx = core.build_context("s1")
        fused = ProductionRealismOrchestrator().build(
            scene_id="s1",
            scene=state.scenes["s1"],
            characters=[state.characters["hero"]],
            world=state.worlds["world"],
            production_context=ctx,
            mood="tense",
            emotional_beats=[{
                "trigger": "door_opens",
                "state": {
                    "primary": "fear",
                    "intensity": 0.7,
                    "cause": "door_opens",
                    "behavior": ["steps back"],
                },
            }],
            atmosphere={
                "lighting": {"source": "moonlight"},
                "environment_sounds": ["wind"],
            },
        )
        self.assertEqual(
            ProductionRealismOrchestrator().validate(fused),
            [],
        )


if __name__ == "__main__":
    unittest.main()
