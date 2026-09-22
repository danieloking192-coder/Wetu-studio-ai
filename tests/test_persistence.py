from wetu_studio import creator_server
from wetu_studio.models.production import CharacterDNA, SceneMemory, WorldDNA

def test_persistent_state_round_trip(tmp_path, monkeypatch):
    state_file = tmp_path / "production_state.json"
    monkeypatch.setattr(creator_server, "STATE_FILE", state_file)
    state = creator_server.CreatorState(project_id="persist-test")
    state.characters["amina"] = CharacterDNA(character_id="amina", name="Amina")
    state.worlds["kinshasa"] = WorldDNA(world_id="kinshasa", name="Kinshasa")
    state.scenes["s1"] = SceneMemory(
        scene_id="s1", project_id="persist-test", sequence=1,
        character_ids=["amina"], world_id="kinshasa"
    )
    state.memory.remember("test", {"value": 1})

    creator_server._persist_state(state)
    restored = creator_server._load_persistent_state()

    assert state_file.exists()
    assert restored.project_id == "persist-test"
    assert restored.characters["amina"].name == "Amina"
    assert restored.worlds["kinshasa"].name == "Kinshasa"
    assert restored.scenes["s1"].character_ids == ["amina"]
    assert restored.memory.events[-1]["type"] == "test"
