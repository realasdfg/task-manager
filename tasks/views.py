from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from tasks.forms import ProjectNameSearchForm, ProjectCreateForm
from tasks.models import Project, Team, Worker, Task


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


class ProjectListView(generic.ListView):
    model = Project

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        project_name = self.request.GET.get("name", "")
        context["search_form"] = ProjectNameSearchForm(
            initial={"name": project_name}
        )
        return context

    def get_queryset(self):
        queryset = Project.objects.all()
        form = ProjectNameSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class ProjectDetailView(generic.DetailView):
    model = Project
    queryset = (Project.objects.all()
                .prefetch_related("teams", "teams__members"))


class ProjectCreateView(generic.CreateView):
    model = Project
    form_class = ProjectCreateForm
