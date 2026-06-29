from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import TaskType, Team, Task

Worker = get_user_model()


class TestWorkerListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
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
        self.assertTrue(self.user == response.context["user"])
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
                self.user,
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


class TestWorkerCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:worker-create"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/workers/create/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:worker-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_create_worker(self):
        self.client.login(username="test_user", password="qwerty")
        form_data = {
            "username": "TestWorker",
            "password1": "azSX1234A",
            "password2": "azSX1234A",
        }

        self.client.post(reverse("tasks:worker-create"), form_data)
        self.assertTrue(
            Worker.objects.filter(username="TestWorker").exists()
        )

    def test_create_worker_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            reverse("tasks:worker-create"),
            {
                "username": "TestWorker",
                "password1": "azSX1234A",
                "password2": "azSX1234A",
            }
        )
        self.assertRedirects(
            response,
            reverse(
                "tasks:worker-detail",
                kwargs={"pk": 2}
            )
        )

    def test_create_worker_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")

        response = self.client.post(
            reverse("tasks:worker-create"),
            {
                "username": "TestWorker",
                "password1": "azSX1234A",
                "password2": "SXaz4321B",
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "password2",
            "The two password fields didn’t match."
        )

    def test_context_has_object_name(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:worker-create"))
        self.assertEqual(response.context["object_name"], "worker")


class TestWorkerUpdateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.url = reverse(
            "tasks:worker-update",
            kwargs={"pk": 2}
        )

    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="test_worker",
            password="azSX1234A",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/workers/{self.worker.id}/update/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_update_worker(self):
        self.client.login(username="test_user", password="qwerty")
        form_data = {
            "username": "test_worker_changed",
            "first_name": "first name",
        }
        self.client.post(self.url, form_data)
        self.assertTrue(
            Worker.objects.filter(username="test_worker_changed").exists()
        )

    def test_update_worker_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            self.url,
            {
                "username": "test_worker_changed",
                "first_name": "first name",
            }
        )
        self.assertRedirects(
            response,
            self.worker.get_absolute_url()
        )

    def test_update_worker_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(self.url, {"first_name": "first name"})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "username",
            "This field is required."
        )

    def test_context_has_object_name(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.url)
        self.assertEqual(response.context["object_name"], "worker")


class TestWorkerDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.url = reverse(
            "tasks:worker-delete",
            kwargs={"pk": 2}
        )

    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="worker",
            password="qwerty",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/workers/{self.worker.id}/delete/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_confirm_delete.html")

    def test_delete_task_type(self):
        self.client.login(username="test_user", password="qwerty")
        self.client.post(self.url)
        self.assertEqual(len(Worker.objects.all()), 1)

    def test_delete_task_type_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:worker-list"))

    def test_success_message_after_deletion(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(self.url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn(self.worker.username, str(messages[0]))
