from wetu_studio.models.project import Project, ProjectStatus, ProjectType


def test_project_defaults_to_idea():
    project = Project("p-001", "Demo", ProjectType.SHORT)
    assert project.status is ProjectStatus.IDEA


def test_project_transition():
    project = Project("p-001", "Demo", ProjectType.AD)
    project.transition_to(ProjectStatus.PREPRODUCTION)
    assert project.status is ProjectStatus.PREPRODUCTION
