from dataclasses import dataclass, field


@dataclass
class WorldBible:
    title: str
    visual_style: str = ""
    tone: str = ""
    locations: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


class WorldBibleEngine:
    def create(self, title: str, visual_style: str = "", tone: str = "") -> WorldBible:
        if not title.strip():
            raise ValueError("title is required")
        return WorldBible(title, visual_style, tone)

    def add_location(self, bible: WorldBible, location: str) -> None:
        if not location.strip():
            raise ValueError("location is required")
        if location not in bible.locations:
            bible.locations.append(location)

    def add_rule(self, bible: WorldBible, rule: str) -> None:
        if not rule.strip():
            raise ValueError("rule is required")
        if rule not in bible.rules:
            bible.rules.append(rule)

    def add_reference(self, bible: WorldBible, reference: str) -> None:
        if not reference.strip():
            raise ValueError("reference is required")
        if reference not in bible.references:
            bible.references.append(reference)
