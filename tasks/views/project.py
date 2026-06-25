from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from task_manager.mixins import SearchMixin
from tasks.forms import (
    ProjectCreateForm,
    ProjectUpdateForm,
    ProjectCompleteForm,
)
from tasks.models import Project


class ProjectListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = Project
    queryset = Project.objects.all().prefetch_related("teams")
    search_fields = {"name": "Search by name", "description": "Search by description"}


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    queryset = (Project.objects.all()
                .prefetch_related("teams", "teams__members"))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)

        project_deadline = self.object.deadline
        context["is_overdue"] = (project_deadline is not None
                                 and project_deadline < timezone.now())
        return context

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        form = ProjectCompleteForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
        return redirect("tasks:project-detail", pk=project.pk)


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectCreateForm


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    form_class = ProjectUpdateForm


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy("tasks:project-list")
