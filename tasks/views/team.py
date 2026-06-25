from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from tasks.forms import TeamNameSearchForm
from tasks.models import Team


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TeamListView, self).get_context_data(**kwargs)
        team_name = self.request.GET.get("name", "")
        context["search_form"] = TeamNameSearchForm(
            initial={"name": team_name}
        )
        return context

    def get_queryset(self):
        queryset = Team.objects.all().prefetch_related("members")
        form = TeamNameSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset
