from django.urls import path

from tasks.views import (
    index,
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
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
]

app_name = "tasks"
