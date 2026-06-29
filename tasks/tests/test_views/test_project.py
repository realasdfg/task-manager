from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tasks.models import Project, Task, TaskType, Team

Worker = get_user_model()


class TestProjectListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.proj_impl1 = Project.objects.create(
            name="Implement smth",
            is_completed=True,
        )
        cls.proj_create = Project.objects.create(name="Create smth")
        cls.proj_impl2 = Project.objects.create(name="Implement smth else")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:project-list"))
        self.assertRedirects(response, "/accounts/login/?next=/projects/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:project-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/project_list.html")

    def test_search_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:project-list"),
            {"name": "implement"}
        )
        self.assertIn(self.proj_impl1, response.context["object_list"])
        self.assertIn(self.proj_impl2, response.context["object_list"])
        self.assertNotIn(self.proj_create, response.context["object_list"])

    def test_sort_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:project-list"),
            {"sort": "-name"}
        )
        self.assertListEqual(
            [self.proj_impl2, self.proj_impl1, self.proj_create],
            list(response.context["object_list"])
        )

    def test_filter_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:project-list"),
            {"status": "completed"}
        )
        self.assertListEqual(
            [self.proj_impl1],
            list(response.context["object_list"])
        )


class TestProjectDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

        cls.project_teams = []
        cls.project_tasks = []
        task_type = TaskType.objects.create(name="task type")
        for i in range(3):
            cls.project_teams.append(
                Team.objects.create(
                    name=f"team_{i}",
                )
            )
            cls.project_tasks.append(
                Task.objects.create(
                    name=f"task_{i}",
                    task_type=task_type,
                )
            )

    def setUp(self):
        self.project = Project.objects.create(
            name="Implement smth",
        )
        self.project.tasks.add(*self.project_tasks)
        self.project.teams.add(*self.project_teams)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.project.get_absolute_url())
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/projects/{self.project.id}/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.project.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/project_detail.html")

    def test_response_contains_teams(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.project.get_absolute_url())

        self.assertContains(response, self.project_teams[0].name)
        self.assertContains(response, self.project_teams[1].name)
        self.assertContains(response, self.project_teams[2].name)

    def test_response_contains_tasks(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.project.get_absolute_url())

        self.assertContains(response, self.project_tasks[0].name)
        self.assertContains(response, self.project_tasks[1].name)
        self.assertContains(response, self.project_tasks[2].name)

    def test_is_overdue_true_when_deadline_in_past(self):
        self.client.login(username="test_user", password="qwerty")

        self.project.deadline = timezone.now() - timedelta(days=1)
        self.project.save()
        response = self.client.get(self.project.get_absolute_url())
        self.assertTrue(response.context["is_overdue"])

    def test_is_overdue_false_when_deadline_in_future(self):
        self.client.login(username="test_user", password="qwerty")

        self.project.deadline = timezone.now() + timedelta(days=1)
        self.project.save()
        response = self.client.get(self.project.get_absolute_url())
        self.assertFalse(response.context["is_overdue"])

    def test_is_overdue_false_when_no_deadline(self):
        self.client.login(username="test_user", password="qwerty")

        self.project.deadline = None
        self.project.save()
        response = self.client.get(self.project.get_absolute_url())
        self.assertFalse(response.context["is_overdue"])

    def test_post_valid_form_saves_and_redirects(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            self.project.get_absolute_url(),
            data={"is_completed": True},
        )
        self.assertRedirects(response, self.project.get_absolute_url())
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_completed)

    def test_post_invalid_form_still_redirects(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            self.project.get_absolute_url()
        )
        self.assertRedirects(response, self.project.get_absolute_url())

    def test_context_contains_tasks(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.project.get_absolute_url())
        self.assertIn("tasks", response.context)


class TestProjectCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:project-create"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/projects/create/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:project-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_create_project(self):
        self.client.login(username="test_user", password="qwerty")
        form_data = {
            "name": "Test Project",
        }

        self.client.post(reverse("tasks:project-create"), form_data)
        self.assertTrue(
            Project.objects.filter(name="Test Project").exists()
        )

    def test_create_project_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            reverse("tasks:project-create"),
            {
                "name": "Test Project",
            },
        )
        self.assertRedirects(
            response,
            reverse(
                "tasks:project-detail",
                kwargs={"pk": 1}
            )
        )

    def test_create_project_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")

        response = self.client.post(
            reverse("tasks:project-create"),
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "name",
            "This field is required."
        )

    def test_context_has_object_name(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:project-create"))
        self.assertEqual(response.context["object_name"], "project")
