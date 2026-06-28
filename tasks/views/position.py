from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin
from tasks.models import Position


class PositionListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = Position
    queryset = Position.objects.all().prefetch_related("workers")
    search_fields = {"name": "Search by name"}
    paginate_by = 10


class PositionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Position
    queryset = Position.objects.all().prefetch_related("workers")


class PositionCreateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.CreateView
):
    model = Position
    fields = ("name",)
    template_name = "tasks/base_form.html"


class PositionUpdateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.UpdateView
):
    model = Position
    fields = ("name",)
    template_name = "tasks/base_form.html"


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("tasks:position-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Position '{self.object}' has been successfully deleted."
        )
        return super().form_valid(form)
