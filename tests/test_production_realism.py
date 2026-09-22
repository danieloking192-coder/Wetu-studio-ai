import unittest

from wetu_studio.models.production import CharacterDNA, SceneMemory, WorldDNA
from wetu_studio.production_realism import ProductionRealismOrchestrator


class ProductionRealismOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = ProductionRealismOrchestrator()
        self.scene = SceneMemory(
            scene_id="scene-1",
            project_id="p1",
            sequence=1,
            character_ids=["hero"],
            world_id="world-1",
        )
        self.character = CharacterDNA(character_id="hero", name="Amina")
        self.world = WorldDNA(world_id="world-1", name="Kinshasa")
    
    def test_fuses_persistent_context_and_emotion(self):
        context = self.orchestrator.build(
            scene_id="scene-1",
            scene=self.scene,
            characters=[self.character],
            world=self.world,
            production_context={"recent_generations": [], "decisions": []},
            mood="tense",
            emotional_beats=[{
                "beat_id": "b1",
                "trigger": "unexpected_news",
                "state": {
                    "primary": "fear",
                    "intensity": 0.8,
                    "cause": "unexpected_news",
                    "behavior": ["breathing becomes shallow"],
                },
            }],
            atmosphere={
                "lighting": {"source": "overcast daylight"},
                "environment_sounds": ["distant traffic"],
            },
        )
        self.assertEqual(context["characters"][0]["name"], "Amina")
        self.assertEqual(context["world"]["name"], "Kinshasa")
        self.assertEqual(context["emotion_continuity"]["mood"], "tense")
        self.assertEqual(context["contract"]["scene_continuity"], "preserve_scene_memory")
        self.assertEqual(self.orchestrator.validate(context), [])

    def test_true_story_requires_provenance_and_dignity_context(self):
        context = self.orchestrator.build(
            scene_id="scene-1",
            scene=self.scene,
            characters=[self.character],
            world=self.world,
            production_context={},
            mood="somber",
            atmosphere={
                "lighting": {"source": "night"},
                "environment_sounds": ["wind"],
            },
            true_story={
                "event": "documented event",
                "facts": [{
                    "fact_id": "f1",
                    "claim": "documented fact",
                    "evidence_class": "verified_fact",
                }],
            },
        )
        issues = self.orchestrator.validate(context)
        self.assertTrue(any("true_story:verified_fact_missing_source:f1" in x for x in issues))
        self.assertTrue(any("true_story:victim_survivor_dignity_context_missing" in x for x in issues))


if __name__ == "__main__":
    unittest.main()
