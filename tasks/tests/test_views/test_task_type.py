from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import TaskType, Task

Worker = get_user_model()


class TestTaskTypeListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.tt_ref = TaskType.objects.create(name="Refactor")
        cls.tt_test = TaskType.objects.create(name="Tests")
        cls.tt_impl = TaskType.objects.create(name="Implement")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:tasktype-list"))
        self.assertRedirects(response, "/accounts/login/?next=/task-types/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:tasktype-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.worker == response.context["user"])
        self.assertTemplateUsed(response, "tasks/tasktype_list.html")

    def test_search_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:tasktype-list"),
            {"name": "impl"}
        )
        self.assertIn(self.tt_impl, response.context["object_list"])
        self.assertNotIn(self.tt_test, response.context["object_list"])
        self.assertNotIn(self.tt_ref, response.context["object_list"])

    def test_sort_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:tasktype-list"),
            {"sort": "-name"}
        )
        self.assertListEqual(
            [self.tt_test, self.tt_ref, self.tt_impl],
            list(response.context["object_list"])
        )


class TestTaskTypeDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

    def setUp(self):
        self.task_type = TaskType.objects.create(
            name="Refactor",
        )
        self.task_type_tasks = []
        for i in range(3):
            self.task_type_tasks.append(
                Task.objects.create(
                    name=f"task_{i}",
                    task_type=self.task_type,
                )
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.task_type.get_absolute_url())
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/task-types/{self.task_type.id}/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.task_type.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.worker == response.context["user"])
        self.assertTemplateUsed(response, "tasks/tasktype_detail.html")

    def test_response_contains_tasks(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.task_type.get_absolute_url())

        self.assertContains(response, self.task_type_tasks[0].name)
        self.assertContains(response, self.task_type_tasks[1].name)
        self.assertContains(response, self.task_type_tasks[2].name)

    def test_context_contains_tasks(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.task_type.get_absolute_url())
        self.assertIn("tasks", response.context)
