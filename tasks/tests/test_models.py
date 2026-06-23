import datetime

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from tasks.models import Position, Worker, TaskType, Task, Project


class TestPosition(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")

    def test_name_unique(self):
        self.assertRaises(
            IntegrityError,
            Position.objects.create,
            name="Developer"
        )

    def test_str(self):
        self.assertEqual(str(self.position), self.position.name)


class TestWorker(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="test_user",
            password="qwerty",
            position=Position.objects.create(name="Developer")
        )

    def test_position_could_be_null(self):
        self.worker.position = None
        self.worker.save()
        self.assertIsNone(self.worker.position)

    def test_str(self):
        self.assertEqual(
            str(self.worker),
            f"{self.worker.first_name} {self.worker.last_name}"
        )


class TestTaskType(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")

    def test_name_unique(self):
        self.assertRaises(
            IntegrityError,
            TaskType.objects.create,
            name="Bug"
        )

    def test_str(self):
        self.assertEqual(str(self.task_type), self.task_type.name)


class TestTask(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")
        self.task = Task.objects.create(
            name="Fix some staff",
            description="Some description",
            deadline=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1),
            task_type=self.task_type,
            project=Project.objects.create(name="Project")
        )

    def test_description_could_be_null(self):
        self.task.description = None
        self.task.save()
        self.assertIsNone(self.task.description)

    def test_deadline_could_be_null(self):
        self.task.deadline = None
        self.task.save()
        self.assertIsNone(self.task.deadline)

    def test_project_could_be_null(self):
        self.task.project = None
        self.task.save()
        self.assertIsNone(self.task.project)

    def test_priority_default(self):
        self.assertEqual(self.task.priority, Task.Priority.MEDIUM)

    def test_priority_choices(self):
        field = Task._meta.get_field("priority")
        choices = [choice[0] for choice in field.choices]

        self.assertIn("urgent", choices)
        self.assertIn("high", choices)
        self.assertIn("medium", choices)
        self.assertIn("low", choices)

    def test_priority_accepts_value(self):
        self.task.priority = Task.Priority.URGENT

        self.assertEqual(self.task.priority, Task.Priority.URGENT)

    def test_task_type_should_be_protected_on_delete(self):
        self.assertRaises(ProtectedError, self.task_type.delete)

    def test_str(self):
        self.assertEqual(str(self.task), self.task.name)
