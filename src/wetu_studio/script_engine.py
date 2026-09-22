from dataclasses import dataclass, field


@dataclass
class Scene:
    scene_id: str
    heading: str
    action: str = ""
    dialogue: list[str] = field(default_factory=list)


@dataclass
class Script:
    title: str
    logline: str = ""
    scenes: list[Scene] = field(default_factory=list)


class ScriptEngine:
    """Deterministic script structure; generation providers are added later."""

    def create_script(self, title: str, logline: str = "") -> Script:
        if not title.strip():
            raise ValueError("title is required")
        return Script(title=title, logline=logline)

    def add_scene(self, script: Script, scene_id: str, heading: str, action: str = "") -> Scene:
        if not scene_id.strip() or not heading.strip():
            raise ValueError("scene_id and heading are required")
        if any(scene.scene_id == scene_id for scene in script.scenes):
            raise ValueError("scene_id must be unique")
        scene = Scene(scene_id=scene_id, heading=heading, action=action)
        script.scenes.append(scene)
        return scene

    def add_dialogue(self, scene: Scene, line: str) -> None:
        if not line.strip():
            raise ValueError("dialogue line is required")
        scene.dialogue.append(line)
