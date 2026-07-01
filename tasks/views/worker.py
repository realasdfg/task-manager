from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin, SortMixin
from tasks.forms import WorkerCreationForm, WorkerUpdateForm
from tasks.mixins import TaskPaginationMixin

Worker = get_user_model()


class WorkerListView(
    SortMixin,
    SearchMixin,
    LoginRequiredMixin,
    generic.ListView
):
    model = Worker
    queryset = (Worker.objects.all()
                .select_related("position")
                .prefetch_related("tasks"))
    search_fields = {
        "username": "Search by username",
        "first_name": "Search by first name",
        "last_name": "Search by last name",
    }
    paginate_by = 10
    sort_options = {
        "username": "Username (A→Z)",
        "-username": "Username (Z→A)",
        "first_name": "Name (A→Z)",
        "-first_name": "Name (Z→A)",
        "last_name": "Surname (A→Z)",
        "-last_name": "Surname (Z→A)",
        "position__name": "Position (A→Z)",
        "-position__name": "Position (Z→A)",
    }
    default_sort = "username"


class WorkerDetailView(
    TaskPaginationMixin,
    LoginRequiredMixin,
    generic.DetailView
):
    model = Worker
    queryset = (Worker.objects.all()
                .select_related("position")
                .prefetch_related("teams"))

    def get_tasks_queryset(self):
        return self.object.tasks.select_related("task_type", "project")


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

    def post(self, request, *args, **kwargs):
        if request.user == self.get_object():
            return redirect(self.get_object().get_absolute_url())
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user == self.get_object():
            return redirect(self.get_object().get_absolute_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Worker '{self.object}' has been successfully deleted."
        )
        return super().form_valid(form)
