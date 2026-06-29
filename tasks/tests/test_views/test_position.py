from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Position

Worker = get_user_model()


class TestPositionListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.pos_front = Position.objects.create(name="Fronted dev")
        cls.pos_back = Position.objects.create(name="Backend dev")
        cls.pos_qa = Position.objects.create(name="QA Engineer")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:position-list"))
        self.assertRedirects(response, "/accounts/login/?next=/positions/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:position-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/position_list.html")

    def test_search_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:position-list"),
            {"name": "front"}
        )
        self.assertIn(self.pos_front, response.context["object_list"])
        self.assertNotIn(self.pos_back, response.context["object_list"])
        self.assertNotIn(self.pos_qa, response.context["object_list"])

    def test_sort_works(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(
            reverse("tasks:position-list"),
            {"sort": "-name"}
        )
        self.assertListEqual(
            [self.pos_qa, self.pos_front, self.pos_back],
            list(response.context["object_list"])
        )


class TestPositionDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.position = Position.objects.create(name="Fronted developer")
        cls.position_workers = []
        for i in range(3):
            cls.position_workers.append(
                Worker.objects.create_user(
                    username=f"test_user_{i}",
                    password="qwerty",
                    position=cls.position,
                )
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.position.get_absolute_url())
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/positions/{self.position.id}/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.position.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/position_detail.html")

    def test_response_contains_workers(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.position.get_absolute_url())

        self.assertContains(response, self.position_workers[0].username)
        self.assertContains(response, self.position_workers[1].username)
        self.assertContains(response, self.position_workers[2].username)
