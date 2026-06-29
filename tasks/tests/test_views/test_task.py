from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tasks.models import Task, TaskType

Worker = get_user_model()


class TestTaskListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
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
        self.assertTrue(self.user == response.context["user"])
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


class TestTaskDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

        cls.task_assignees = []
        cls.task_type = TaskType.objects.create(name="task type")
        for i in range(3):
            cls.task_assignees.append(
                Worker.objects.create_user(
                    username=f"worker_{i}",
                    password="qwerty",
                )
            )

    def setUp(self):
        self.task = Task.objects.create(
            name="Implement smth",
            task_type=self.task_type,
        )
        self.task.assignees.add(*self.task_assignees)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.task.get_absolute_url())
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/tasks/{self.task.id}/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.task.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/task_detail.html")

    def test_response_contains_assignees(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.task.get_absolute_url())

        self.assertContains(response, self.task_assignees[0].username)
        self.assertContains(response, self.task_assignees[1].username)
        self.assertContains(response, self.task_assignees[2].username)

    def test_is_overdue_true_when_deadline_in_past(self):
        self.client.login(username="test_user", password="qwerty")

        self.task.deadline = timezone.now() - timedelta(days=1)
        self.task.save()
        response = self.client.get(self.task.get_absolute_url())
        self.assertTrue(response.context["is_overdue"])

    def test_is_overdue_false_when_deadline_in_future(self):
        self.client.login(username="test_user", password="qwerty")

        self.task.deadline = timezone.now() + timedelta(days=1)
        self.task.save()
        response = self.client.get(self.task.get_absolute_url())
        self.assertFalse(response.context["is_overdue"])

    def test_is_overdue_false_when_no_deadline(self):
        self.client.login(username="test_user", password="qwerty")

        self.task.deadline = None
        self.task.save()
        response = self.client.get(self.task.get_absolute_url())
        self.assertFalse(response.context["is_overdue"])

    def test_post_valid_form_saves_and_redirects(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            self.task.get_absolute_url(),
            data={"is_completed": True},
        )
        self.assertRedirects(response, self.task.get_absolute_url())
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_completed)

    def test_post_invalid_form_still_redirects(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            self.task.get_absolute_url()
        )
        self.assertRedirects(response, self.task.get_absolute_url())


class TestProjectCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.task_type = TaskType.objects.create(name="task type")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:task-create"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/tasks/create/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:task-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_create_task(self):
        self.client.login(username="test_user", password="qwerty")
        form_data = {
            "name": "Test Task",
            "task_type": self.task_type.id,
            "priority": "medium",
        }

        self.client.post(reverse("tasks:task-create"), form_data)
        self.assertTrue(
            Task.objects.filter(name="Test Task").exists()
        )

    def test_create_task_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            reverse("tasks:task-create"),
            {
                "name": "Test Task",
                "task_type": self.task_type.id,
                "priority": "medium",
            }
        )
        self.assertRedirects(
            response,
            reverse(
                "tasks:task-detail",
                kwargs={"pk": 1}
            )
        )

    def test_create_task_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")

        response = self.client.post(
            reverse("tasks:task-create"),
            {
                "name": "Test Task",
                "priority": "medium",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "task_type",
            "This field is required."
        )

    def test_context_has_object_name(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:task-create"))
        self.assertEqual(response.context["object_name"], "task")
