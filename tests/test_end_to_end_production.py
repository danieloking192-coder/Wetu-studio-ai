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
        self.assertTrue(result["pipeline"]["continuity_preflight"])
        self.assertEqual(result["continuity"][0]["checked_references"], 0)

    def test_continuity_reuses_previous_scene_references(self):
        chars=[CharacterDNA(character_id="hero",name="A")]
        world=WorldDNA(world_id="w",name="W")
        scenes1=[SceneMemory(scene_id="s1",project_id="p",sequence=1,character_ids=["hero"],world_id="w")]
        scenes2=[SceneMemory(scene_id="s2",project_id="p",sequence=2,character_ids=["hero"],world_id="w")]
        orch=WetuCreativeOrchestrator(media=MediaRegistry())
        first=orch.produce(project_id="p",brief="A cinematic scene",characters=chars,world=world,
                           scenes=scenes1,provider="wetu-local",kind="image")
        second=orch.produce(project_id="p",brief="Continue the same scene",characters=chars,world=world,
                            scenes=scenes2,provider="wetu-local",kind="image")
        self.assertEqual(first["assets"][0]["status"],"generated")
        self.assertEqual(second["assets"][0]["status"],"generated")
        self.assertGreaterEqual(second["continuity"][0]["checked_references"], 2)
        self.assertIn("memory://wetu/p/p:s1:image/image", second["assets"][0]["asset"]["metadata"]["references"])
