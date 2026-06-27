from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin
from tasks.forms import WorkerCreationForm, WorkerUpdateForm
from tasks.mixins import PaginationMixin

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
    paginate_by = 10


class WorkerDetailView(
    PaginationMixin,
    LoginRequiredMixin,
    generic.DetailView
):
    model = Worker
    queryset = (Worker.objects.all()
                .select_related("position")
                .prefetch_related("teams"))
    paginate_by = 10
    page_kwarg = "tasks_page"
    pagination_context_name = "tasks"

    def get_pagination_queryset(self):
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

    def form_valid(self, form):
        messages.success(self.request, f"Worker '{self.object.name}' has been successfully deleted.")
        return super().form_valid(form)
