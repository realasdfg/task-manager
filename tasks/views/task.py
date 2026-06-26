from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from task_manager.mixins import SearchMixin
from tasks.forms import TaskCompleteForm, TaskForm
from tasks.models import Task


class TaskListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = Task
    queryset = (Task.objects.all()
                .prefetch_related("assignees")
                .select_related("task_type", "project"))
    search_fields = {"name": "Search by name"}


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = (Task.objects.all()
                .select_related("project", "task_type")
                .prefetch_related("assignees__position", "assignees__teams"))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)

        task_deadline = self.object.deadline
        context["is_overdue"] = (task_deadline is not None
                                 and task_deadline < timezone.now())
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        form = TaskCompleteForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
        return redirect("tasks:task-detail", pk=task.pk)


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("tasks:task-list")
