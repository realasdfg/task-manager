from datetime import timedelta

from django import forms
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.views import generic

from task_manager.mixins import SearchMixin, SortMixin, AddObjectNameMixin
from tasks.mixins import (
    PaginationMixin,
    DeadlineValidationMixin,
    TaskPaginationMixin,
)
from tasks.models import Position, TaskType, Task


class DummySearchView(SearchMixin, generic.ListView):
    model = Position
    search_fields = {"name": "Search by name"}
    template_name = "tasks/base_list.html"


class TestSearchMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        Position.objects.create(name="Developer")
        Position.objects.create(name="Manager")
        Position.objects.create(name="QA Engineer")

    def test_no_query_returns_all(self):
        request = self.factory.get("/fake-url/")
        view = DummySearchView()
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 3)

    def test_filters_by_search(self):
        request = self.factory.get("/fake-url/", {"name": "dev"})
        view = DummySearchView()
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().name, "Developer")

    def test_no_match_returns_empty(self):
        request = self.factory.get("/fake-url/", {"name": "nonexistent"})
        view = DummySearchView()
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 0)

    def test_invalid_form_returns_unfiltered_queryset(self):
        request = self.factory.get("/fake-url/", {"unknown_field": "x"})
        view = DummySearchView()
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 3)

    def test_context_contains_search_form(self):
        request = self.factory.get("/fake-url/")
        view = DummySearchView()
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn("search_form", context)


class DummySortView(SortMixin, generic.ListView):
    model = Position
    sort_options = {
        "name": "Name (A→Z)",
        "-name": "Name (Z→A)",
    }
    default_sort = "name"
    template_name = "tasks/base_list.html"


class TestSortMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.pos_qa = Position.objects.create(name="QA Engineer")
        cls.pos_dev = Position.objects.create(name="Developer")
        cls.pos_man = Position.objects.create(name="Manager")

    def test_no_query_returns_sorted_by_default(self):
        request = self.factory.get("/fake-url/")
        view = DummySortView()
        view.request = request
        queryset = view.get_queryset()
        self.assertListEqual(
            list(queryset.all()),
            [self.pos_dev, self.pos_man, self.pos_qa]
        )

    def test_sorts_by_param(self):
        request = self.factory.get("/fake-url/", {"sort": "-name"})
        view = DummySortView()
        view.request = request
        queryset = view.get_queryset()
        self.assertListEqual(
            list(queryset.all()),
            [self.pos_qa, self.pos_man, self.pos_dev]
        )

    def test_no_match_returns_default(self):
        request = self.factory.get("/fake-url/", {"sort": "nonexistent"})
        view = DummySortView()
        view.request = request
        queryset = view.get_queryset()
        self.assertListEqual(
            list(queryset.all()),
            [self.pos_dev, self.pos_man, self.pos_qa]
        )

    def test_empty_returns_default(self):
        request = self.factory.get("/fake-url/", {"sort": ""})
        view = DummySortView()
        view.request = request
        queryset = view.get_queryset()
        self.assertListEqual(
            list(queryset.all()),
            [self.pos_dev, self.pos_man, self.pos_qa]
        )

    def test_invalid_form_returns_default(self):
        request = self.factory.get("/fake-url/", {"unknown_field": "x"})
        view = DummySortView()
        view.request = request
        queryset = view.get_queryset()
        self.assertListEqual(
            list(queryset.all()),
            [self.pos_dev, self.pos_man, self.pos_qa]
        )

    def test_context_contains_sort_options(self):
        request = self.factory.get("/fake-url/")
        view = DummySortView()
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn("sort_options", context)

    def test_context_contains_current_sort(self):
        request = self.factory.get("/fake-url/")
        view = DummySortView()
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn("current_sort", context)


class DummyAddObjectNameView(AddObjectNameMixin, generic.ListView):
    model = Position
    template_name = "tasks/base_list.html"


class TestAddObjectNameMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def test_adds_object_name_to_context(self):
        request = self.factory.get("/fake-url/")
        view = DummyAddObjectNameView()
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn("object_name", context)
        self.assertEqual("position", context["object_name"])


class DummyPaginationView(PaginationMixin, generic.DetailView):
    model = Position
    paginate_by = 2
    pagination_context_name = "items"

    def get_pagination_queryset(self):
        return Position.objects.all()


class TestPaginationMixin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        for i in range(5):
            Position.objects.create(name=f"Position {i}")
        self.position = Position.objects.first()

    def _make_view(self, page=None):
        params = {"page": page} if page else {}
        request = self.factory.get("/fake-url/", params)
        view = DummyPaginationView()
        view.request = request
        view.object = self.position
        view.kwargs = {}
        return view

    def test_first_page_contains_correct_number_of_items(self):
        view = self._make_view()
        context = view.get_context_data()
        self.assertEqual(len(context["items"]), 2)

    def test_second_page_returns_next_items(self):
        view = self._make_view(page=2)
        context = view.get_context_data()
        self.assertEqual(len(context["items"]), 2)

    def test_last_page_returns_remaining_items(self):
        view = self._make_view(page=3)
        context = view.get_context_data()
        self.assertEqual(len(context["items"]), 1)

    def test_items_count_added_to_context(self):
        view = self._make_view()
        context = view.get_context_data()
        self.assertEqual(context["items_count"], 5)

    def test_invalid_page_returns_last_page(self):
        view = self._make_view(page=999)
        context = view.get_context_data()
        self.assertIsNotNone(context["items"])

    def test_not_implemented_error_without_override(self):
        class BrokenView(PaginationMixin, generic.DetailView):
            model = Position

        request = self.factory.get("/fake-url/")
        view = BrokenView()
        view.request = request
        view.object = self.position
        view.kwargs = {}
        with self.assertRaises(NotImplementedError):
            view.get_context_data()


class DummyTaskView(TaskPaginationMixin, generic.DetailView):
    model = Position

    def get_tasks_queryset(self):
        return Task.objects.all()


class TestTaskPaginationMixin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.position = Position.objects.create(name="Developer")
        self.task_type = TaskType.objects.create(name="Bug")

        self.task_completed = Task.objects.create(
            name="Done Task",
            is_completed=True,
            task_type=self.task_type,
            created_at=timezone.now() - timedelta(days=2),
        )
        self.task_uncompleted = Task.objects.create(
            name="Active Task",
            is_completed=False,
            task_type=self.task_type,
            created_at=timezone.now(),
        )

    def _make_view(self, params=None):
        request = self.factory.get("/fake-url/", params or {})
        view = DummyTaskView()
        view.request = request
        view.object = self.position
        view.kwargs = {}
        return view

    def test_filter_completed_returns_only_completed(self):
        view = self._make_view({"status": "completed"})
        queryset = view.get_pagination_queryset()
        self.assertTrue(all(t.is_completed for t in queryset))
        self.assertIn(self.task_completed, queryset)
        self.assertNotIn(self.task_uncompleted, queryset)

    def test_filter_uncompleted_returns_only_uncompleted(self):
        view = self._make_view({"status": "uncompleted"})
        queryset = view.get_pagination_queryset()
        self.assertFalse(any(t.is_completed for t in queryset))

    def test_invalid_status_returns_all_tasks(self):
        view = self._make_view({"status": "invalid"})
        queryset = view.get_pagination_queryset()
        self.assertEqual(queryset.count(), 2)

    def test_no_status_returns_all_tasks(self):
        view = self._make_view()
        queryset = view.get_pagination_queryset()
        self.assertEqual(queryset.count(), 2)

    def test_default_sort_is_created_at_desc(self):
        view = self._make_view()
        queryset = view.get_pagination_queryset()
        self.assertEqual(queryset.first(), self.task_uncompleted)

    def test_sort_by_name_asc(self):
        view = self._make_view({"sort": "name"})
        queryset = view.get_pagination_queryset()
        self.assertEqual(queryset.first().name, "Active Task")

    def test_sort_by_name_desc(self):
        view = self._make_view({"sort": "-name"})
        queryset = view.get_pagination_queryset()
        self.assertEqual(queryset.first().name, "Done Task")

    def test_invalid_sort_sort_by_default(self):
        view = self._make_view({"sort": "invalid"})
        queryset = view.get_pagination_queryset()
        self.assertEqual(queryset.count(), 2)

    def test_context_contains_sort_options(self):
        view = self._make_view()
        context = view.get_context_data()
        self.assertEqual(
            context["sort_options"],
            TaskPaginationMixin.TASKS_SORT_OPTIONS
        )

    def test_context_current_sort_default(self):
        view = self._make_view()
        context = view.get_context_data()
        self.assertEqual(context["current_sort"], "-created_at")

    def test_context_current_sort_from_request(self):
        view = self._make_view({"sort": "name"})
        context = view.get_context_data()
        self.assertEqual(context["current_sort"], "name")

    def test_context_current_status_empty_by_default(self):
        view = self._make_view()
        context = view.get_context_data()
        self.assertEqual(context["current_status"], "")

    def test_context_current_status_from_request(self):
        view = self._make_view({"status": "completed"})
        context = view.get_context_data()
        self.assertEqual(context["current_status"], "completed")

    def test_not_implemented_error_without_override(self):
        class BrokenView(TaskPaginationMixin, generic.DetailView):
            model = Position

        request = self.factory.get("/fake-url/")
        view = BrokenView()
        view.request = request
        view.object = self.position
        view.kwargs = {}
        with self.assertRaises(NotImplementedError):
            view.get_pagination_queryset()


class DummyForm(DeadlineValidationMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ("name", "deadline")


class TestDeadlineValidationMixin(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")
        self.task = Task.objects.create(
            name="Existing Task",
            task_type=self.task_type,
            deadline=timezone.now() + timedelta(days=5),
        )
        self.future = timezone.now() + timedelta(days=3)
        self.past = timezone.now() - timedelta(days=1)

    def test_no_deadline_is_valid(self):
        form = DummyForm({"name": "Task", "deadline": ""}, instance=self.task)
        form.is_valid()
        self.assertNotIn("deadline", form.errors)

    def test_future_deadline_on_create_is_valid(self):
        form = DummyForm({"name": "Task", "deadline": self.future})
        self.assertTrue(form.is_valid())

    def test_past_deadline_on_create_raises_error(self):
        form = DummyForm({"name": "Task", "deadline": self.past})
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Deadline cannot be in the past",
            form.errors["deadline"]
        )

    def test_same_deadline_on_update_is_valid(self):
        form = DummyForm(
            {"name": "Task", "deadline": self.task.deadline},
            instance=self.task,
        )
        self.assertTrue(form.is_valid())

    def test_new_future_deadline_on_update_is_valid(self):
        form = DummyForm(
            {"name": "Task", "deadline": self.future},
            instance=self.task,
        )
        self.assertTrue(form.is_valid())

    def test_new_past_deadline_on_update_raises_error(self):
        form = DummyForm(
            {"name": "Task", "deadline": self.past},
            instance=self.task,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Deadline cannot be in the past",
            form.errors["deadline"]
        )
