from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from tasks.models import Project, Team, Worker, Task


@login_required
def index(request: HttpRequest) -> HttpResponse:
    num_projects = Project.objects.count()
    num_teams = Team.objects.count()
    num_workers = Worker.objects.count()
    num_tasks = Task.objects.count()
    context = {
        "num_projects": num_projects,
        "num_teams": num_teams,
        "num_workers": num_workers,
        "num_tasks": num_tasks,
    }
    return render(request, "tasks/index.html", context=context)
