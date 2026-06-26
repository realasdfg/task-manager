from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin
from tasks.models import TaskType


class TaskTypeListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = TaskType
    queryset = TaskType.objects.all().prefetch_related("tasks")
    search_fields = {"name": "Search by name"}


class TaskTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = TaskType
    queryset = TaskType.objects.all().prefetch_related("tasks")


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = ("name",)


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    fields = ("name",)


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
