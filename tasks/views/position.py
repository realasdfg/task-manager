from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin
from tasks.models import Position


class PositionListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = Position
    queryset = Position.objects.all().prefetch_related("workers")
    search_fields = {"name": "Search by name"}


class PositionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Position
    queryset = Position.objects.all().prefetch_related("workers")


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = ("name",)


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Position
    fields = ("name",)


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("tasks:position-list")
