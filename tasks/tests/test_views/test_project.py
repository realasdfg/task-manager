from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Project

Worker = get_user_model()


class TestProjectListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.worker = Worker.objects.create_user(
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
        self.assertTrue(self.worker == response.context["user"])
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
