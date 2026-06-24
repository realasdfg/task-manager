from django.urls import path

from tasks.views import index, ProjectListView

urlpatterns = [
    path("", index, name="index"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
]

app_name = "tasks"
