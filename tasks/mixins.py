from django import forms
from django.core.paginator import Paginator
from django.utils import timezone


class DeadlineValidationMixin:
    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline is None:
            return deadline

        original_deadline = getattr(self.instance, "deadline", None)
        deadline_changed = original_deadline != deadline

        if deadline_changed and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past")
        return deadline


class PaginationMixin:
    """
    Mixin for paginating a queryset in a DetailView.

    Subclasses must implement `get_paginated_queryset()`.

    Attributes:
        paginate_by (int):
            Number of objects displayed per page.
        page_kwarg (str):
            Name of the GET parameter that stores the page number.
        pagination_context_name (str):
            Context variable containing the paginated Page object.
            The total number of objects is also added as
            `<context_object_name>_count`.
    """
    paginate_by = 10
    page_kwarg = "page"
    pagination_context_name = "objects"

    def get_pagination_queryset(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(
            self.get_pagination_queryset(),
            self.paginate_by,
        )
        page = self.request.GET.get(self.page_kwarg)
        context[self.pagination_context_name] = paginator.get_page(page)
        context[f"{self.pagination_context_name}_count"] = paginator.count

        return context


class TaskPaginationMixin(PaginationMixin):
    paginate_by = 10
    page_kwarg = "tasks_page"
    pagination_context_name = "tasks"

    TASKS_SORT_OPTIONS = {
        "name": "Name (A→Z)",
        "-name": "Name (Z→A)",
        "deadline": "Deadline (earliest)",
        "-deadline": "Deadline (latest)",
        "created_at": "Creation (earliest)",
        "-created_at": "Creation (latest)",
    }

    TASKS_FILTER_OPTIONS = {
        "completed": True,
        "uncompleted": False,
    }

    def get_tasks_queryset(self):
        raise NotImplementedError

    def get_pagination_queryset(self):
        queryset = self.get_tasks_queryset()

        status = self.request.GET.get("status")
        if status in self.TASKS_FILTER_OPTIONS:
            queryset = queryset.filter(
                is_completed=self.TASKS_FILTER_OPTIONS[status]
            )

        sort = self.request.GET.get("sort", "-created_at")
        if sort in self.TASKS_SORT_OPTIONS:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort_options"] = self.TASKS_SORT_OPTIONS
        context["current_sort"] = self.request.GET.get("sort", "-created_at")
        context["filter_options"] = self.TASKS_FILTER_OPTIONS
        context["current_status"] = self.request.GET.get("status", "")
        return context