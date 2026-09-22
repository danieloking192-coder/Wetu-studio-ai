from dataclasses import dataclass, field

@dataclass
class Shot:
    shot_id: str
    scene_id: str
    shot_type: str = ""
    description: str = ""
    characters: list[str] = field(default_factory=list)
    location: str = ""
    wardrobe_by_character: dict[str, str] = field(default_factory=dict)

@dataclass
class Storyboard:
    title: str
    shots: list[Shot] = field(default_factory=list)

class StoryboardEngine:
    def create(self, title: str) -> Storyboard:
        if not title.strip(): raise ValueError("title is required")
        return Storyboard(title=title)

    def add_shot(self, storyboard: Storyboard, shot_id: str, scene_id: str, shot_type: str = "", description: str = "") -> Shot:
        if not shot_id.strip() or not scene_id.strip(): raise ValueError("shot_id and scene_id are required")
        if any(s.shot_id == shot_id for s in storyboard.shots): raise ValueError("shot_id must be unique")
        shot = Shot(shot_id, scene_id, shot_type, description)
        storyboard.shots.append(shot)
        return shot

    def add_character(self, shot: Shot, character_id: str) -> None:
        if not character_id.strip(): raise ValueError("character_id is required")
        if character_id not in shot.characters: shot.characters.append(character_id)

    def set_wardrobe(self, shot: Shot, character_id: str, outfit: str) -> None:
        if character_id not in shot.characters: raise ValueError("character must be assigned to the shot")
        if not outfit.strip(): raise ValueError("outfit is required")
        shot.wardrobe_by_character[character_id] = outfit
