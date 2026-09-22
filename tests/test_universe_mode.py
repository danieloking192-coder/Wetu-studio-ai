from wetu_studio.universe_mode import UniverseMode, UniverseProduction

def test_fan_film_accepts_referenced_characters():
    project = UniverseProduction("p1", "Fan Short", UniverseMode.FAN_FILM)
    ref = project.add_ip_character("naruto", "Naruto Uzumaki", "Naruto Shippuden")
    assert ref.source_work == "Naruto Shippuden"
    assert project.validate() == []

def test_original_universe_rejects_ip_character_references():
    project = UniverseProduction("p2", "WETU Saga", UniverseMode.ORIGINAL)
    try:
        project.add_ip_character("naruto", "Naruto Uzumaki", "Naruto Shippuden")
    except ValueError:
        pass
    else:
        raise AssertionError("ORIGINAL mode must reject IP character references")

def test_original_universe_can_attach_its_own_universe():
    project = UniverseProduction("p3", "WETU Saga", UniverseMode.ORIGINAL)
    project.attach_original_universe("universe-wetu-001")
    assert project.original_universe_id == "universe-wetu-001"
    assert project.validate() == []