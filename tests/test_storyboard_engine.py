from wetu_studio.storyboard_engine import StoryboardEngine

def test_storyboard_character_and_wardrobe():
    e = StoryboardEngine(); sb = e.create("Film")
    shot = e.add_shot(sb, "S1", "SC1", "CLOSE_UP", "Portrait")
    e.add_character(shot, "hero")
    e.set_wardrobe(shot, "hero", "black suit")
    assert shot.wardrobe_by_character["hero"] == "black suit"
