from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Task, TaskType

Worker = get_user_model()


class TestTaskListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

        task_type = TaskType.objects.create(name="test_task_type")
        cls.task_impl1 = Task.objects.create(
            name="Implement smth",
            task_type=task_type,
            is_completed=True
        )
        cls.task_create = Task.objects.create(
            name="Create smth",
            task_type=task_type
        )
        cls.task_impl2 = Task.objects.create(
            name="Implement smth else",
            task_type=task_type
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:task-list"))
        self.assertRedirects(response, "/accounts/login/?next=/tasks/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:task-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.worker == response.context["user"])
        self.assertTemplateUsed(response, "tasks/task_list.html")

    def test_search_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:task-list"),
            {"name": "implement"}
        )
        self.assertIn(self.task_impl1, response.context["object_list"])
        self.assertIn(self.task_impl2, response.context["object_list"])
        self.assertNotIn(self.task_create, response.context["object_list"])

    def test_sort_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:task-list"),
            {"sort": "-name"}
        )
        self.assertListEqual(
            [self.task_impl2, self.task_impl1, self.task_create],
            list(response.context["object_list"])
        )

    def test_filter_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:task-list"),
            {"status": "completed"}
        )
        self.assertListEqual(
            [self.task_impl1],
            list(response.context["object_list"])
        )
