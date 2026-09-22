from .models.project import Project, ProjectStatus, ProjectType


class ProjectStudio:
    """Create and manage projects without external services."""

    def create(self, project_id: str, title: str, project_type: ProjectType, synopsis: str = "") -> Project:
        if not project_id.strip():
            raise ValueError("project_id is required")
        if not title.strip():
            raise ValueError("title is required")
        return Project(project_id=project_id, title=title, project_type=project_type, synopsis=synopsis)

    def start_preproduction(self, project: Project) -> Project:
        if project.status is not ProjectStatus.IDEA:
            raise ValueError("Project must be in IDEA state")
        project.transition_to(ProjectStatus.PREPRODUCTION)
        return project
