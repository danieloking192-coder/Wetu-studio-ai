from wetu_studio.universe_mode import UniverseMode, UniverseProduction

def test_naruto_shippuden_characters_are_explicit_fan_film_references():
    project = UniverseProduction("naruto-short-001", "Naruto Shippuden — WETU Fan Short", UniverseMode.FAN_FILM)
    for character_id, name in (("naruto-uzumaki", "Naruto Uzumaki"), ("sasuke-uchiha", "Sasuke Uchiha"), ("sakura-haruno", "Sakura Haruno"), ("kakashi-hatake", "Kakashi Hatake")):
        project.add_ip_character(character_id, name, "Naruto Shippuden", notes="User-selected fan-film reference")
    assert len(project.character_references) == 4
    assert project.validate() == []