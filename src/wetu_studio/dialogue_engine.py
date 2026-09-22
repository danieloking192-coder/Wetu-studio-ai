from dataclasses import dataclass, field

@dataclass
class DialogueLine:
    speaker_id: str
    text: str
    language: str = "fr"
    translation: dict[str, str] = field(default_factory=dict)

@dataclass
class Dialogue:
    dialogue_id: str
    lines: list[DialogueLine] = field(default_factory=list)

class DialogueEngine:
    SUPPORTED_LANGUAGES = {"fr", "en", "es", "pt", "ar", "sw", "ln"}

    def create(self, dialogue_id: str) -> Dialogue:
        if not dialogue_id.strip():
            raise ValueError("dialogue_id is required")
        return Dialogue(dialogue_id)

    def add_line(self, dialogue: Dialogue, speaker_id: str, text: str, language: str = "fr") -> DialogueLine:
        if not speaker_id.strip() or not text.strip():
            raise ValueError("speaker_id and text are required")
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError("unsupported language")
        line = DialogueLine(speaker_id, text, language)
        dialogue.lines.append(line)
        return line

    def add_translation(self, line: DialogueLine, language: str, text: str) -> None:
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError("unsupported language")
        if not text.strip():
            raise ValueError("translation is required")
        line.translation[language] = text
