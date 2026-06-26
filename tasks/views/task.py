from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from task_manager.mixins import SearchMixin
from tasks.models import Task


class TaskListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = Task
    queryset = Task.objects.all()
    search_fields = {"name": "Search by name"}
