from wetu_studio.dialogue_engine import DialogueEngine

def test_multilingual_dialogue():
    e = DialogueEngine()
    d = e.create("d1")
    line = e.add_line(d, "hero", "Bonjour.", "fr")
    e.add_translation(line, "en", "Hello.")
    e.add_line(d, "friend", "Hello.", "en")
    assert line.translation["en"] == "Hello."
