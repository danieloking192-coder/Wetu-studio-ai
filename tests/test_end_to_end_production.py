import unittest
from wetu_studio.creative_orchestrator import WetuCreativeOrchestrator
from wetu_studio.media_engine import MediaRegistry
from wetu_studio.models.production import CharacterDNA, SceneMemory, WorldDNA

class EndToEndProductionTests(unittest.TestCase):
    def test_plan_and_produce_scene(self):
        chars=[CharacterDNA(character_id="hero",name="A")]
        world=WorldDNA(world_id="w",name="W")
        scenes=[SceneMemory(scene_id="s1",project_id="p",sequence=1,character_ids=["hero"],world_id="w")]
        result=WetuCreativeOrchestrator(media=MediaRegistry()).produce(
            project_id="p",brief="A cinematic scene",characters=chars,world=world,
            scenes=scenes,provider="wetu-local",kind="image")
        self.assertEqual(result["assets"][0]["status"],"generated")
        self.assertFalse(result["assets"][0]["asset"]["metadata"]["real_media"])
        self.assertTrue(result["pipeline"]["qa_before_generation"])
