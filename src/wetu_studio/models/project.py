from dataclasses import dataclass, field
from enum import Enum


class ProjectType(str, Enum):
    AD = "AD"
    SHORT = "SHORT"
    FILM = "FILM"
    SERIES = "SERIES"
    EPISODE = "EPISODE"
    MUSIC_VIDEO = "MUSIC_VIDEO"
    SOCIAL = "SOCIAL"


class ProjectStatus(str, Enum):
    IDEA = "IDEA"
    PREPRODUCTION = "PREPRODUCTION"
    GENERATION = "GENERATION"
    EDITING = "EDITING"
    QA = "QA"
    READY = "READY"
    PUBLISHED = "PUBLISHED"


@dataclass
class Project:
    project_id: str
    title: str
    project_type: ProjectType
    status: ProjectStatus = ProjectStatus.IDEA
    synopsis: str = ""
    tags: list[str] = field(default_factory=list)

    def transition_to(self, status: ProjectStatus) -> None:
        self.status = status
