from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin
from tasks.models import TaskType


class TaskTypeListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = TaskType
    queryset = TaskType.objects.all().prefetch_related("tasks")
    search_fields = {"name": "Search by name"}


class TaskTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = TaskType
    queryset = TaskType.objects.all().prefetch_related("tasks")


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
        messages.success(self.request, f"Task type '{self.object.name}' has been successfully deleted.")
        return super().form_valid(form)
