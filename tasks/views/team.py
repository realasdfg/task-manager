from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from task_manager.mixins import SearchMixin, AddObjectNameMixin
from tasks.forms import TeamForm
from tasks.models import Team


class TeamListView(SearchMixin, LoginRequiredMixin, generic.ListView):
    model = Team
    queryset = Team.objects.all().prefetch_related("members")
    search_fields = {"name": "Search by name"}
    paginate_by = 10


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team
    queryset = (Team.objects.all().prefetch_related(
        "members", "members__position", "members__tasks"
    ))


class TeamCreateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.CreateView
):
    model = Team
    form_class = TeamForm
    template_name = "tasks/base_form.html"


class TeamUpdateView(
    AddObjectNameMixin,
    LoginRequiredMixin,
    generic.UpdateView
):
    model = Team
    form_class = TeamForm
    template_name = "tasks/base_form.html"


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    template_name = "tasks/base_confirm_delete.html"
    success_url = reverse_lazy("tasks:team-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Team '{self.object.name}' has been successfully deleted."
        )
        return super().form_valid(form)
