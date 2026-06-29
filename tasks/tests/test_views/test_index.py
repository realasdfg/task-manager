from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Project, Team, Task, TaskType

Worker = get_user_model()


class TestIndexView(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:index"))
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.worker == response.context["user"])
        self.assertTemplateUsed(response, "tasks/index.html")

    def test_num_workers(self):
        self.client.login(username="test_user", password="qwerty")
        for i in range(5):
            Worker.objects.create_user(
                username=f"test_user{i}",
                password="qwerty",
            )
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.context["num_workers"], 6)

    def test_num_projects(self):
        self.client.login(username="test_user", password="qwerty")

        for i in range(5):
            Project.objects.create(
                name=f"project{i}",
            )
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.context["num_projects"], 5)

    def test_num_teams(self):
        self.client.login(username="test_user", password="qwerty")
        for i in range(5):
            Team.objects.create(
                name=f"team{i}",
            )
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.context["num_teams"], 5)

    def test_num_tasks(self):
        self.client.login(username="test_user", password="qwerty")
        task_type = TaskType.objects.create(name="task_type")
        for i in range(5):
            Task.objects.create(
                name=f"team{i}",
                task_type=task_type
            )
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.context["num_tasks"], 5)
