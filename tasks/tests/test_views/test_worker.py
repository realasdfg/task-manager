from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import TaskType, Team, Task

Worker = get_user_model()


class TestWorkerListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.worker_billy = Worker.objects.create_user(
            username="billy_bob",
            password="qwerty"
        )
        cls.worker_big = Worker.objects.create_user(
            username="big_bob",
            password="qwerty"
        )
        cls.worker_lena = Worker.objects.create_user(
            username="lena_123",
            password="qwerty"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:worker-list"))
        self.assertRedirects(response, "/accounts/login/?next=/workers/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:worker-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.worker == response.context["user"])
        self.assertTemplateUsed(response, "tasks/worker_list.html")

    def test_search_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:worker-list"),
            {"username": "bob"}
        )
        self.assertIn(self.worker_big, response.context["object_list"])
        self.assertIn(self.worker_billy, response.context["object_list"])
        self.assertNotIn(self.worker_lena, response.context["object_list"])

    def test_sort_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:worker-list"),
            {"sort": "-username"}
        )
        self.assertListEqual(
            [
                self.worker,
                self.worker_lena,
                self.worker_billy,
                self.worker_big
            ],
            list(response.context["object_list"])
        )


class TestWorkerDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

        cls.worker_teams = []
        cls.worker_tasks = []
        task_type = TaskType.objects.create(name="task type")
        for i in range(3):
            cls.worker_teams.append(
                Team.objects.create(
                    name=f"team_{i}",
                )
            )
            cls.worker_tasks.append(
                Task.objects.create(
                    name=f"task_{i}",
                    task_type=task_type,
                )
            )

    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="worker",
            password="qwerty",
        )
        self.worker.tasks.add(*self.worker_tasks)
        self.worker.teams.add(*self.worker_teams)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.worker.get_absolute_url())
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/workers/{self.worker.id}/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.worker.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/worker_detail.html")

    def test_response_contains_teams(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.worker.get_absolute_url())

        self.assertContains(response, self.worker_teams[0].name)
        self.assertContains(response, self.worker_teams[1].name)
        self.assertContains(response, self.worker_teams[2].name)

    def test_response_contains_tasks(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.worker.get_absolute_url())

        self.assertContains(response, self.worker_tasks[0].name)
        self.assertContains(response, self.worker_tasks[1].name)
        self.assertContains(response, self.worker_tasks[2].name)

    def test_context_contains_tasks(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.worker.get_absolute_url())
        self.assertIn("tasks", response.context)
