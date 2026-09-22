from wetu_studio.models.project import ProjectStatus, ProjectType
from wetu_studio.studio import ProjectStudio


def test_create_project():
    project = ProjectStudio().create("p-001", "Demo", ProjectType.SHORT)
    assert project.status is ProjectStatus.IDEA
    assert project.title == "Demo"


def test_start_preproduction():
    project = ProjectStudio().create("p-001", "Demo", ProjectType.AD)
    ProjectStudio().start_preproduction(project)
    assert project.status is ProjectStatus.PREPRODUCTION
