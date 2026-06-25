from tasks.forms import SearchForm


class SearchMixin:
    """
    Mixin for ListView that adds name-based search functionality.

    Attributes:
        search_fields (dict): A mapping of field names
            to their placeholder text.
            Example: {"name": "Search by name",
            "description": "Search by description"}

    Example usage:
        class ProjectListView(SearchMixin, generic.ListView):
            model = Project
            search_fields = {"name": "Search by name"}
    """
    search_fields: dict = {}

    def get_search_form(self):
        return SearchForm(self.request.GET or None, fields=self.search_fields)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = self.get_search_form()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_search_form()
        if form.is_valid():
            for field_name in self.search_fields:
                value = form.cleaned_data.get(field_name)
                if value:
                    queryset = queryset.filter(
                        **{f"{field_name}__icontains": value}
                    )
        return queryset
