from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django_select2.forms import Select2MultipleWidget

from tasks.models import Project, Team, Worker


class ProjectBaseForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "deadline", "teams",)
        widgets = {
            "teams": Select2MultipleWidget,
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"})
        }


class ProjectCreateForm(ProjectBaseForm):
    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past")
        return deadline


class ProjectUpdateForm(ProjectBaseForm):
    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline is None:
            return deadline

        original_deadline = self.instance.deadline
        deadline_changed = original_deadline != deadline
        if deadline_changed and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past")
        return deadline


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
