import unittest
from wetu_studio.models.production import CharacterDNA, SceneMemory, WorldDNA
from wetu_studio.creative_orchestrator import WetuCreativeOrchestrator

class CreativeOrchestratorTests(unittest.TestCase):
    def test_brief_becomes_persistent_scene_plan(self):
        chars=[CharacterDNA(character_id="hero", name="Amina")]
        world=WorldDNA(world_id="w", name="Kinshasa")
        scenes=[SceneMemory(scene_id="s1", project_id="p", sequence=1,
                            character_ids=["hero"], world_id="w")]
        result=WetuCreativeOrchestrator().plan(
            project_id="p", brief="Une histoire de survie.",
            characters=chars, world=world, scenes=scenes)
        self.assertEqual(result["project_id"], "p")
        self.assertEqual(result["scenes"][0]["status"], "ready")
        self.assertTrue(result["rendering"]["provider_neutral"])
        self.assertTrue(result["rendering"]["requires_real_provider"])

    def test_empty_brief_is_rejected(self):
        with self.assertRaises(ValueError):
            WetuCreativeOrchestrator().plan(
                project_id="p", brief=" ", characters=[
                    CharacterDNA(character_id="hero", name="A")],
                world=WorldDNA(world_id="w", name="W"),
                scenes=[SceneMemory(scene_id="s", project_id="p", sequence=1)])
