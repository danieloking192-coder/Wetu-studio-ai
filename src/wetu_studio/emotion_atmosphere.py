"""Emotion and atmosphere engine for WETU scene direction.

Turns narrative intent into a deterministic, provider-neutral scene brief.
It does not render media; it prepares the emotional, physical and sensory
conditions that a renderer must preserve.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class EmotionalState:
    primary: str
    intensity: float = 0.7
    secondary: List[str] = field(default_factory=list)
    valence: float = 0.0
    arousal: float = 0.5
    cause: str = ""
    bodily_signals: List[str] = field(default_factory=list)
    micro_expressions: List[str] = field(default_factory=list)
    behavior: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.intensity = max(0.0, min(1.0, float(self.intensity)))
        self.valence = max(-1.0, min(1.0, float(self.valence)))
        self.arousal = max(0.0, min(1.0, float(self.arousal)))


@dataclass
class AtmosphereState:
    time_of_day: str = "unspecified"
    weather: str = "unspecified"
    temperature_feel: str = "neutral"
    air: str = "natural"
    lighting: Dict[str, Any] = field(default_factory=dict)
    environment_sounds: List[str] = field(default_factory=list)
    ambient_motion: List[str] = field(default_factory=list)
    smells: List[str] = field(default_factory=list)
    physical_details: List[str] = field(default_factory=list)


@dataclass
class EmotionalBeat:
    beat_id: str
    trigger: str
    state: EmotionalState
    duration_hint: str = "natural"
    continuity_key: str = ""


@dataclass
class SceneAtmosphere:
    scene_id: str
    mood: str
    emotional_beats: List[EmotionalBeat] = field(default_factory=list)
    atmosphere: AtmosphereState = field(default_factory=AtmosphereState)
    sensory_focus: List[str] = field(default_factory=list)
    camera_guidance: List[str] = field(default_factory=list)
    continuity_notes: List[str] = field(default_factory=list)
    realism_constraints: List[str] = field(default_factory=list)
    source_vs_interpretation: str = "artistic_direction"


class EmotionAtmosphereEngine:
    """Build and validate a production-grade emotional scene context."""

    DEFAULT_CONSTRAINTS = [
        "emotion must have a visible or behavioral cause",
        "micro-expressions must remain consistent with the emotional state",
        "ambient motion and sound must respect the physical environment",
        "lighting must match time, weather and location",
        "emotional continuity must persist unless a new event explains the change",
        "do not substitute exaggerated expressions for credible human behavior",
    ]

    def build(
        self,
        *,
        scene_id: str,
        mood: str,
        beats: List[Dict[str, Any]] | None = None,
        atmosphere: Dict[str, Any] | None = None,
        sensory_focus: List[str] | None = None,
        camera_guidance: List[str] | None = None,
        continuity_notes: List[str] | None = None,
        source_vs_interpretation: str = "artistic_direction",
    ) -> SceneAtmosphere:
        parsed: List[EmotionalBeat] = []
        for index, item in enumerate(beats or []):
            raw = item.get("state", item)
            state = EmotionalState(
                primary=str(raw.get("primary", "neutral")),
                intensity=raw.get("intensity", 0.5),
                secondary=list(raw.get("secondary", [])),
                valence=raw.get("valence", 0.0),
                arousal=raw.get("arousal", 0.5),
                cause=str(raw.get("cause", item.get("trigger", ""))),
                bodily_signals=list(raw.get("bodily_signals", [])),
                micro_expressions=list(raw.get("micro_expressions", [])),
                behavior=list(raw.get("behavior", [])),
            )
            parsed.append(EmotionalBeat(
                beat_id=str(item.get("beat_id", f"beat-{index+1}")),
                trigger=str(item.get("trigger", state.cause)),
                state=state,
                duration_hint=str(item.get("duration_hint", "natural")),
                continuity_key=str(item.get("continuity_key", "")),
            ))
        return SceneAtmosphere(
            scene_id=scene_id,
            mood=mood,
            emotional_beats=parsed,
            atmosphere=AtmosphereState(**(atmosphere or {})),
            sensory_focus=list(sensory_focus or []),
            camera_guidance=list(camera_guidance or []),
            continuity_notes=list(continuity_notes or []),
            realism_constraints=list(self.DEFAULT_CONSTRAINTS),
            source_vs_interpretation=source_vs_interpretation,
        )

    def validate(self, scene: SceneAtmosphere) -> List[str]:
        issues: List[str] = []
        for beat in scene.emotional_beats:
            if not beat.state.cause and not beat.trigger:
                issues.append(f"{beat.beat_id}: missing emotional cause")
            if beat.state.intensity > 0.85 and not (beat.state.bodily_signals or beat.state.behavior):
                issues.append(f"{beat.beat_id}: high-intensity emotion lacks physical behavior")
            if beat.state.micro_expressions and not beat.state.bodily_signals and not beat.state.behavior:
                issues.append(f"{beat.beat_id}: micro-expressions lack a behavioral anchor")
        if not scene.atmosphere.lighting:
            issues.append("missing lighting context")
        if not scene.atmosphere.environment_sounds:
            issues.append("missing environmental sound context")
        return issues

    def continuity_snapshot(self, scene: SceneAtmosphere) -> Dict[str, Any]:
        beats = []
        for beat in scene.emotional_beats:
            beats.append({
                "beat_id": beat.beat_id,
                "primary": beat.state.primary,
                "intensity": beat.state.intensity,
                "valence": beat.state.valence,
                "arousal": beat.state.arousal,
                "continuity_key": beat.continuity_key,
            })
        return {"scene_id": scene.scene_id, "mood": scene.mood, "beats": beats}

    def to_dict(self, scene: SceneAtmosphere) -> Dict[str, Any]:
        return asdict(scene)
