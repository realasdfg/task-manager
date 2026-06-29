from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Team

Worker = get_user_model()


class TestTeamListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.team_back = Team.objects.create(name="Backend team")
        cls.team_front = Team.objects.create(name="Frontend team")
        cls.team_qa = Team.objects.create(name="QA team")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:team-list"))
        self.assertRedirects(response, "/accounts/login/?next=/teams/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:team-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.worker == response.context["user"])
        self.assertTemplateUsed(response, "tasks/team_list.html")

    def test_search_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:team-list"),
            {"name": "end"}
        )
        self.assertIn(self.team_back, response.context["object_list"])
        self.assertIn(self.team_front, response.context["object_list"])
        self.assertNotIn(self.team_qa, response.context["object_list"])

    def test_sort_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:team-list"),
            {"sort": "-name"}
        )
        self.assertListEqual(
            [self.team_qa, self.team_front, self.team_back],
            list(response.context["object_list"])
        )


class TestTeamDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.team = Team.objects.create(name="Fronted team")
        cls.team_members = []
        for i in range(3):
            cls.team_members.append(
                Worker.objects.create_user(
                    username=f"test_user_{i}",
                    password="qwerty",
                )
            )
        cls.team.members.add(*cls.team_members)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.team.get_absolute_url())
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/teams/{self.team.id}/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.team.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.worker == response.context["user"])
        self.assertTemplateUsed(response, "tasks/team_detail.html")

    def test_response_contains_members(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.team.get_absolute_url())

        self.assertContains(response, self.team_members[0].username)
        self.assertContains(response, self.team_members[1].username)
        self.assertContains(response, self.team_members[2].username)
