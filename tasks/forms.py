from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_select2.forms import Select2MultipleWidget

from tasks.mixins import DeadlineValidationMixin
from tasks.models import Project, Team, Worker, Task


class ProjectForm(DeadlineValidationMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "deadline", "teams",)
        widgets = {
            "teams": Select2MultipleWidget,
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"})
        }


class ProjectCompleteForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("is_completed",)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("name", "members",)
        widgets = {
            "members": Select2MultipleWidget,
        }


class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "position",
        )


class WorkerUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ("username", "first_name", "last_name", "email", "position",)


class TaskCompleteForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("is_completed",)


class TaskForm(DeadlineValidationMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "name",
            "task_type",
            "priority",
            "description",
            "project",
            "deadline",
            "assignees",
        )
        widgets = {
            "assignees": Select2MultipleWidget,
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"})
        }


class SearchForm(forms.Form):
    def __init__(self, *args, fields: dict, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, placeholder in fields.items():
            self.fields[field_name] = forms.CharField(
                max_length=255,
                required=False,
                label="",
                widget=forms.TextInput(attrs={"placeholder": placeholder})
            )
