from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin
from tasks.forms import WorkerCreationForm, WorkerUpdateForm

Worker = get_user_model()


class WorkerListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = Worker
    queryset = (Worker.objects.all()
                .select_related("position")
                .prefetch_related("tasks"))
    search_fields = {
        "username": "Search by username",
        "first_name": "Search by first name",
        "last_name": "Search by last name",
    }


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    queryset = (Worker.objects.all()
                .select_related("position")
                .prefetch_related("tasks__task_type", "teams"))


class WorkerCreateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.CreateView
):
    model = Worker
    form_class = WorkerCreationForm
    template_name = "tasks/base_form.html"


class WorkerUpdateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.UpdateView
):
    model = Worker
    form_class = WorkerUpdateForm
    template_name = "tasks/base_form.html"


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    template_name = "tasks/base_confirm_delete.html"
    success_url = reverse_lazy("tasks:worker-list")
