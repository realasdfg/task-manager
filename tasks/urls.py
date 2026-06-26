from django.urls import path

from tasks.views.index import index
from tasks.views.position import (
    PositionListView,
    PositionDetailView,
    PositionCreateView,
    PositionUpdateView,
    PositionDeleteView,
)
from tasks.views.project import (
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView
)
from tasks.views.task import (
    TaskListView,
)
from tasks.views.task_type import (
    TaskTypeListView,
    TaskTypeDetailView,
    TaskTypeCreateView,
    TaskTypeUpdateView,
    TaskTypeDeleteView,
)
from tasks.views.team import (
    TeamListView,
    TeamDetailView,
    TeamCreateView,
    TeamUpdateView,
    TeamDeleteView,
)
from tasks.views.worker import (
    WorkerListView,
    WorkerDetailView,
    WorkerCreateView,
    WorkerUpdateView,
    WorkerDeleteView,
)

urlpatterns = [
    path("", index, name="index"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path(
        "projects/<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail"
    ),
    path(
        "projects/create/",
        ProjectCreateView.as_view(),
        name="project-create"
    ),
    path(
        "projects/<int:pk>/update/",
        ProjectUpdateView.as_view(),
        name="project-update"
    ),
    path(
        "projects/<int:pk>/delete/",
        ProjectDeleteView.as_view(),
        name="project-delete"
    ),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path(
        "teams/<int:pk>/update",
        TeamUpdateView.as_view(),
        name="team-update"
    ),
    path(
        "teams/<int:pk>/delete",
        TeamDeleteView.as_view(),
        name="team-delete"
    ),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path(
        "workers/<int:pk>/",
        WorkerDetailView.as_view(),
        name="worker-detail"
    ),
    path(
        "workers/create/",
        WorkerCreateView.as_view(),
        name="worker-create"
    ),
    path(
        "workers/<int:pk>/update/",
        WorkerUpdateView.as_view(),
        name="worker-update"
    ),
    path(
        "workers/<int:pk>/delete/",
        WorkerDeleteView.as_view(),
        name="worker-delete"
    ),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path(
        "positions/<int:pk>/",
        PositionDetailView.as_view(),
        name="position-detail"
    ),
    path(
        "positions/create/",
        PositionCreateView.as_view(),
        name="position-create"
    ),
    path(
        "positions/<int:pk>/update/",
        PositionUpdateView.as_view(),
        name="position-update"
    ),
    path(
        "positions/<int:pk>/delete/",
        PositionDeleteView.as_view(),
        name="position-delete"
    ),
    path("task-types/", TaskTypeListView.as_view(), name="tasktype-list"),
    path(
        "task-types/<int:pk>/",
        TaskTypeDetailView.as_view(),
        name="tasktype-detail"
    ),
    path(
        "task-types/create/",
        TaskTypeCreateView.as_view(),
        name="tasktype-create"
    ),
    path(
        "task-types/<int:pk>/update/",
        TaskTypeUpdateView.as_view(),
        name="tasktype-update"
    ),
    path(
        "task-types/<int:pk>/delete/",
        TaskTypeDeleteView.as_view(),
        name="tasktype-delete"
    ),
    path("tasks/", TaskListView.as_view(), name="task-list"),
]

app_name = "tasks"
