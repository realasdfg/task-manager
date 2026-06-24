from django.urls import path

from tasks.views import (
    index,
    ProjectListView,
    ProjectDetailView
)

urlpatterns = [
    path("", index, name="index"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path(
        "projects/<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail"
    ),
]

app_name = "tasks"
