import datetime

from django import forms
from django.test import TestCase
from django.utils import timezone
from django_select2.forms import Select2MultipleWidget

from tasks.forms import (
    LoginForm,
    ProjectForm,
    ProjectCompleteForm,
    TeamForm, WorkerCreationForm, WorkerUpdateForm, TaskCompleteForm, TaskForm, SearchForm,
)
from tasks.models import Team, Project, Worker, Position, TaskType, Task


class LoginFormTest(TestCase):
    def test_form_fields_have_form_control_class(self):
        form = LoginForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs["class"])


class ProjectFormTest(TestCase):
    def test_is_valid(self):
        deadline = timezone.now() + datetime.timedelta(days=1)
        form_data = {
            "name": "Project",
            "description": "Project description",
            "deadline": deadline,
            "teams": [
                Team.objects.create(name="team1").id,
                Team.objects.create(name="team2").id
            ],
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

        project = form.save()
        self.assertEqual(project.name, "Project")
        self.assertEqual(project.description, "Project description")
        self.assertEqual(project.deadline, deadline)
        self.assertEqual(
            list(project.teams.values_list("id", flat=True)),
            form_data["teams"]
        )

    def test_deadline_cannot_be_in_the_past_while_create(self):
        deadline = timezone.now() - datetime.timedelta(days=1)
        form_data = {
            "name": "Project",
            "deadline": deadline,
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_deadline_cannot_be_changed_to_past_while_update(self):
        project = Project.objects.create(
            name="Project",
            deadline=timezone.now() - datetime.timedelta(days=1)
        )
        earlier_deadline = timezone.now() - datetime.timedelta(days=5)
        form_data = {
            "name": "Project",
            "deadline": earlier_deadline,
        }
        form = ProjectForm(data=form_data, instance=project)
        self.assertFalse(form.is_valid())

    def test_deadline_can_be_in_the_past_if_not_changed(self):
        project = Project.objects.create(
            name="Project",
            deadline=timezone.now() - datetime.timedelta(days=1)
        )
        form_data = {
            "name": "Project123",
        }
        form = ProjectForm(data=form_data, instance=project)
        self.assertTrue(form.is_valid())

    def test_teams_field_uses_multiple_widget(self):
        form = ProjectForm()
        self.assertTrue(isinstance(
            form.fields["teams"].widget,
            Select2MultipleWidget
        ))

    def test_deadline_field_uses_date_time_input_widget(self):
        form = ProjectForm()
        self.assertTrue(isinstance(
            form.fields["deadline"].widget,
            forms.DateTimeInput
        ))


class ProjectCompleteFormTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Project")

    def test_can_mark_project_as_completed(self):
        form = ProjectCompleteForm(
            data={"is_completed": True},
            instance=self.project
        )
        self.assertTrue(form.is_valid())

        form.save()
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_completed)

    def test_can_mark_project_as_not_completed(self):
        form = ProjectCompleteForm(
            data={"is_completed": False},
            instance=self.project
        )
        self.assertTrue(form.is_valid())

        form.save()
        self.project.refresh_from_db()
        self.assertFalse(self.project.is_completed)


class TeamFormTest(TestCase):
    def test_is_valid(self):
        form_data = {
            "name": "Team",
            "members": [
                Worker.objects.create_user(
                    username="worker1",
                    password="qwerty"
                ).id,
                Worker.objects.create_user(
                    username="worker2",
                    password="qwerty"
                ).id,
            ],
        }
        form = TeamForm(data=form_data)
        self.assertTrue(form.is_valid())

        team = form.save()
        self.assertEqual(team.name, "Team")
        self.assertEqual(
            list(team.members.values_list("id", flat=True)),
            form_data["members"]
        )

    def test_members_field_uses_multiple_widget(self):
        form = TeamForm()
        self.assertTrue(isinstance(
            form.fields["members"].widget,
            Select2MultipleWidget
        ))


class TestWorkerCreationForm(TestCase):
    def test_with_additional_fields(self):
        position = Position.objects.create(name="Position")
        form_data = {
            "username": "worker1",
            "password1": "fhgkA1754",
            "password2": "fhgkA1754",
            "first_name": "Bobby",
            "last_name": "Bob",
            "email": "bob@example.com",
            "position": position,
        }
        form = WorkerCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

        worker = form.save()
        self.assertEqual(worker.username, "worker1")
        self.assertTrue(worker.check_password("fhgkA1754"))
        self.assertEqual(worker.first_name, "Bobby")
        self.assertEqual(worker.last_name, "Bob")
        self.assertEqual(worker.email, "bob@example.com")
        self.assertEqual(worker.position, position)


class TestWorkerUpdateForm(TestCase):
    def test_is_valid(self):
        position = Position.objects.create(name="Position")
        form_data = {
            "username": "worker1",
            "first_name": "Bobby",
            "last_name": "Bob",
            "email": "bob@example.com",
            "position": position,
        }
        form = WorkerUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)


class TaskCompleteFormTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            name="Task",
            task_type=TaskType.objects.create(name="TaskType"),
        )

    def test_can_mark_task_as_completed(self):
        form = TaskCompleteForm(
            data={"is_completed": True},
            instance=self.task
        )
        self.assertTrue(form.is_valid())

        form.save()
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_completed)

    def test_can_mark_task_as_not_completed(self):
        form = TaskCompleteForm(
            data={"is_completed": False},
            instance=self.task
        )
        self.assertTrue(form.is_valid())

        form.save()
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_completed)


class TaskFormTest(TestCase):
    def test_is_valid(self):
        task_type = TaskType.objects.create(name="TaskType")
        project = Project.objects.create(name="Project")
        deadline = timezone.now() + datetime.timedelta(days=1)
        form_data = {
            "name": "Task",
            "task_type": task_type,
            "priority": "urgent",
            "description": "Task Description",
            "project": project,
            "deadline": deadline,
            "assignees": [
                Worker.objects.create_user(
                    username="worker1",
                    password="qwerty"
                ).id,
                Worker.objects.create_user(
                    username="worker2",
                    password="qwerty"
                ).id,
            ],
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

        task = form.save()
        self.assertEqual(task.name, "Task")
        self.assertEqual(task.task_type, task_type)
        self.assertEqual(task.priority, "urgent")
        self.assertEqual(task.description, "Task Description")
        self.assertEqual(task.project, project)
        self.assertEqual(task.deadline, deadline)
        self.assertEqual(
            list(task.assignees.values_list("id", flat=True)),
            form_data["assignees"]
        )

    def test_deadline_cannot_be_in_the_past_while_create(self):
        deadline = timezone.now() - datetime.timedelta(days=1)
        form_data = {
            "name": "Task",
            "deadline": deadline,
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_deadline_cannot_be_changed_to_past_while_update(self):
        task_type = TaskType.objects.create(name="TaskType")
        task = Task.objects.create(
            name="Task",
            task_type=task_type,
            deadline=timezone.now() - datetime.timedelta(days=1)
        )
        earlier_deadline = timezone.now() - datetime.timedelta(days=5)
        form_data = {
            "name": "Task",
            "task_type": task_type,
            "deadline": earlier_deadline,
        }
        form = TaskForm(data=form_data, instance=task)
        self.assertFalse(form.is_valid())

    def test_deadline_can_be_in_the_past_if_not_changed(self):
        task_type = TaskType.objects.create(name="TaskType")
        task = Task.objects.create(
            name="Task",
            task_type=task_type,
            priority="urgent",
            deadline=timezone.now() - datetime.timedelta(days=1)
        )
        form_data = {
            "name": "Task123",
            "task_type": task_type,
            "priority": "low",
        }
        form = TaskForm(data=form_data, instance=task)
        self.assertTrue(form.is_valid())

    def test_assignees_field_uses_multiple_widget(self):
        form = TaskForm()
        self.assertTrue(isinstance(
            form.fields["assignees"].widget,
            Select2MultipleWidget
        ))

    def test_deadline_field_uses_date_time_input_widget(self):
        form = TaskForm()
        self.assertTrue(isinstance(
            form.fields["deadline"].widget,
            forms.DateTimeInput
        ))


class TestSearchForm(TestCase):
    def test_fields_are_created_with_correct_placeholders(self):
        fields = {
            "name": "Search by name",
            "description": "Search by description"
        }
        form = SearchForm(fields=fields)

        for field_name, placeholder in fields.items():
            self.assertIn(field_name, form.fields)
            self.assertEqual(
                form.fields[field_name].widget.attrs["placeholder"],
                placeholder
            )

    def test_all_fields_are_not_required(self):
        form = SearchForm(fields={"name": "Search by name"})
        self.assertFalse(form.fields["name"].required)

    def test_form_is_valid_with_empty_data(self):
        form = SearchForm(
            data={"search": ""},
            fields={"name": "Search by name"}
        )
        self.assertTrue(form.is_valid())
