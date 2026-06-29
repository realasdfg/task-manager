from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Team

Worker = get_user_model()


class TestTeamListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
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
        self.assertTrue(self.user == response.context["user"])
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
        cls.user = Worker.objects.create_user(
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
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/team_detail.html")

    def test_response_contains_members(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.team.get_absolute_url())

        self.assertContains(response, self.team_members[0].username)
        self.assertContains(response, self.team_members[1].username)
        self.assertContains(response, self.team_members[2].username)


class TestTeamCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:team-create"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/teams/create/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:team-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_create_team(self):
        self.client.login(username="test_user", password="qwerty")
        form_data = {
            "name": "Test Team",
        }

        self.client.post(reverse("tasks:team-create"), form_data)
        self.assertTrue(
            Team.objects.filter(name="Test Team").exists()
        )

    def test_create_team_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            reverse("tasks:team-create"),
            {
                "name": "Test Team",
            }
        )
        self.assertRedirects(
            response,
            reverse(
                "tasks:team-detail",
                kwargs={"pk": 1}
            )
        )

    def test_create_team_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")

        response = self.client.post(
            reverse("tasks:team-create"),
            {}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "name",
            "This field is required."
        )

    def test_context_has_object_name(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:team-create"))
        self.assertEqual(response.context["object_name"], "team")


class TestTeamUpdateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

    def setUp(self):
        self.team = Team.objects.create(name="Test Team")

    def test_redirect_if_not_logged_in(self):
        url = reverse(
            "tasks:team-update",
            kwargs={"pk": self.team.id}
        )
        response = self.client.get(url)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/teams/{self.team.id}/update/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        url = reverse(
            "tasks:team-update",
            kwargs={"pk": self.team.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_update_team(self):
        self.client.login(username="test_user", password="qwerty")
        url = reverse(
            "tasks:team-update",
            kwargs={"pk": self.team.id}
        )
        form_data = {"name": "Test Team Changed"}
        self.client.post(url, form_data)
        self.assertTrue(
            Team.objects.filter(name="Test Team Changed").exists()
        )

    def test_update_team_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        url = reverse(
            "tasks:team-update",
            kwargs={"pk": self.team.id}
        )
        response = self.client.post(url, {"name": "Test Team Changed"})
        self.assertRedirects(
            response,
            self.team.get_absolute_url()
        )

    def test_update_team_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")
        url = reverse(
            "tasks:team-update",
            kwargs={"pk": self.team.id}
        )
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "name",
            "This field is required."
        )

    def test_context_has_object_name(self):
        self.client.login(username="test_user", password="qwerty")
        url = reverse(
            "tasks:team-update",
            kwargs={"pk": self.team.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.context["object_name"], "team")
