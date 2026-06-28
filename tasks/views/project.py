from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin, SortMixin
from tasks.forms import ProjectForm, ProjectCompleteForm
from tasks.mixins import PaginationMixin
from tasks.models import Project


class ProjectListView(
    SortMixin,
    SearchMixin,
    LoginRequiredMixin,
    generic.ListView
):
    model = Project
    queryset = Project.objects.all().prefetch_related("teams")
    search_fields = {"name": "Search by name",
                     "description": "Search by description"}
    paginate_by = 10
    sort_options = {
        "name": "Name (A→Z)",
        "-name": "Name (Z→A)",
        "deadline": "Deadline (earliest)",
        "-deadline": "Deadline (latest)",
        "created_at": "Creation (earliest)",
        "-created_at": "Creation (latest)",
        "-is_completed": "Completed first",
        "is_completed": "Uncompleted first",
    }
    default_sort = "-created_at"


class ProjectDetailView(
    PaginationMixin,
    LoginRequiredMixin,
    generic.DetailView
):
    model = Project
    queryset = Project.objects.prefetch_related("teams__members")
    paginate_by = 10
    page_kwarg = "tasks_page"
    pagination_context_name = "tasks"

    def get_pagination_queryset(self):
        return self.object.tasks.select_related("task_type")

    def get_context_data(self, **kwargs):
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


class ProjectCreateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.CreateView
):
    model = Project
    form_class = ProjectForm
    template_name = "tasks/base_form.html"


class ProjectUpdateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.UpdateView
):
    model = Project
    form_class = ProjectForm
    template_name = "tasks/base_form.html"


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy("tasks:project-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Project '{self.object}' has been successfully deleted."
        )
        return super().form_valid(form)
