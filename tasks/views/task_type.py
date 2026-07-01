from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin, SortMixin
from tasks.mixins import PaginationMixin
from tasks.models import TaskType


class TaskTypeListView(
    SortMixin,
    SearchMixin,
    LoginRequiredMixin,
    generic.ListView
):
    model = TaskType
    queryset = TaskType.objects.all().prefetch_related("tasks")
    search_fields = {"name": "Search by name"}
    paginate_by = 10
    sort_options = {
        "name": "Name (A→Z)",
        "-name": "Name (Z→A)",
    }
    default_sort = "name"


class TaskTypeDetailView(
    PaginationMixin,
    LoginRequiredMixin,
    generic.DetailView
):
    model = TaskType
    paginate_by = 10
    page_kwarg = "tasks_page"
    pagination_context_name = "tasks"

    def get_pagination_queryset(self):
        return (
            self.object.tasks
            .select_related("project")
            .prefetch_related("assignees")
        )


class TaskTypeCreateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.CreateView
):
    model = TaskType
    fields = ("name",)
    template_name = "tasks/base_form.html"


class TaskTypeUpdateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.UpdateView
):
    model = TaskType
    fields = ("name",)
    template_name = "tasks/base_form.html"


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    success_url = reverse_lazy("tasks:tasktype-list")
    queryset = TaskType.objects.all().prefetch_related("tasks")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "Cannot delete: used by existing tasks.")
            return redirect("tasks:tasktype-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Task type '{self.object}' has been successfully deleted."
        )
        return super().form_valid(form)
