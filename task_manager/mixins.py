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


class SortMixin:
    sort_options = {}
    default_sort = ""

    def get_sort_options(self):
        return self.sort_options

    def get_current_sort(self):
        sort = self.request.GET.get("sort", self.default_sort)
        return sort if sort in self.get_sort_options() else self.default_sort

    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.get_current_sort()
        if sort:
            queryset = queryset.order_by(sort)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort_options"] = self.get_sort_options()
        context["current_sort"] = self.get_current_sort()
        return context


class FilterMixin:
    filter_fields = {}  # {"url_param": ("field", {"option": value})}

    def get_filter_fields(self):
        return self.filter_fields

    def get_active_filters(self):
        active = {}
        for param, (field, options) in self.get_filter_fields().items():
            value = self.request.GET.get(param)
            if value in options:
                active[param] = value
        return active

    def get_queryset(self):
        queryset = super().get_queryset()
        for param, (field, options) in self.get_filter_fields().items():
            value = self.request.GET.get(param)
            if value in options:
                queryset = queryset.filter(**{field: options[value]})
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_fields"] = self.get_filter_fields()
        context["active_filters"] = self.get_active_filters()
        return context


class AddObjectNameMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_name"] = self.model._meta.verbose_name
        return context
