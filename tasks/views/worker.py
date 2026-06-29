from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin, SortMixin
from tasks.forms import WorkerCreationForm, WorkerUpdateForm
from tasks.mixins import PaginationMixin

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

    SORT_OPTIONS = {
        "name": "Name (A→Z)",
        "-name": "Name (Z→A)",
        "deadline": "Deadline (earliest)",
        "-deadline": "Deadline (latest)",
        "created_at": "Creation (earliest)",
        "-created_at": "Creation (latest)",
    }

    FILTER_OPTIONS = {
        "completed": True,
        "uncompleted": False,
    }

    def get_pagination_queryset(self):
        queryset = self.object.tasks.select_related("task_type", "project")

        # filter
        status = self.request.GET.get("status")
        if status in self.FILTER_OPTIONS:
            queryset = queryset.filter(is_completed=self.FILTER_OPTIONS[status])

        # sort
        sort = self.request.GET.get("sort", "-created_at")
        if sort in self.SORT_OPTIONS:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort_options"] = self.SORT_OPTIONS
        context["current_sort"] = self.request.GET.get("sort", "-created_at")
        context["filter_options"] = self.FILTER_OPTIONS
        context["current_status"] = self.request.GET.get("status", "")
        return context


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
        messages.success(
            self.request,
            f"Worker '{self.object}' has been successfully deleted."
        )
        return super().form_valid(form)
