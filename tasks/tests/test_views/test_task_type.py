from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import TaskType, Task

Worker = get_user_model()


class TestTaskTypeListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
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
        self.assertTrue(self.user == response.context["user"])
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
        cls.user = Worker.objects.create_user(
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
        self.assertTrue(self.user == response.context["user"])
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


class TestTaskTypeCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("tasks:tasktype-create"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/task-types/create/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(reverse("tasks:tasktype-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_create_task_type(self):
        self.client.login(username="test_user", password="qwerty")
        form_data = {
            "name": "Test Task Type",
        }

        self.client.post(reverse("tasks:tasktype-create"), form_data)
        self.assertTrue(
            TaskType.objects.filter(name="Test Task Type").exists()
        )

    def test_create_task_type_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            reverse("tasks:tasktype-create"),
            {
                "name": "Test Task Type",
            }
        )
        self.assertRedirects(
            response,
            reverse(
                "tasks:tasktype-detail",
                kwargs={"pk": 1}
            )
        )

    def test_create_task_type_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")

        response = self.client.post(
            reverse("tasks:tasktype-create"),
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
        response = self.client.get(reverse("tasks:tasktype-create"))
        self.assertEqual(response.context["object_name"], "task type")


class TestTaskTypeUpdateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.url = reverse(
            "tasks:tasktype-update",
            kwargs={"pk": 1}
        )

    def setUp(self):
        self.task_type = TaskType.objects.create(name="Test TaskType")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/task-types/{self.task_type.id}/update/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(response, "tasks/base_form.html")

    def test_update_task_type(self):
        self.client.login(username="test_user", password="qwerty")
        form_data = {"name": "Test TaskType Changed"}
        self.client.post(self.url, form_data)
        self.assertTrue(
            TaskType.objects.filter(name="Test TaskType Changed").exists()
        )

    def test_update_task_type_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(
            self.url,
            {"name": "Test TaskType Changed"}
        )
        self.assertRedirects(
            response,
            self.task_type.get_absolute_url(),
        )

    def test_update_task_type_invalid_data(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "name",
            "This field is required."
        )

    def test_context_has_object_name(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.url)
        self.assertEqual(response.context["object_name"], "task type")


class TestTaskTypeDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
        )
        cls.url = reverse(
            "tasks:tasktype-delete",
            kwargs={"pk": 1}
        )

    def setUp(self):
        self.task_type = TaskType.objects.create(
            name="Test TaskType",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/task-types/{self.task_type.id}/delete/"
        )

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user == response.context["user"])
        self.assertTemplateUsed(
            response,
            "tasks/tasktype_confirm_delete.html"
        )

    def test_delete_task_type(self):
        self.client.login(username="test_user", password="qwerty")
        self.client.post(self.url)
        self.assertEqual(len(TaskType.objects.all()), 0)

    def test_cannot_delete_task_type_when_tasks_exist(self):
        Task.objects.create(name="Test Task", task_type=self.task_type)
        self.client.login(username="test_user", password="qwerty")
        self.client.post(self.url)
        self.assertEqual(len(TaskType.objects.all()), 1)

    def test_delete_task_type_redirect(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:tasktype-list"))

    def test_success_message_after_deletion(self):
        self.client.login(username="test_user", password="qwerty")
        response = self.client.post(self.url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn(self.task_type.name, str(messages[0]))
