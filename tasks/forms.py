from django import forms
from django_select2.forms import Select2MultipleWidget

from tasks.models import Project, Team


class ProjectCreateForm(forms.ModelForm):
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        required=False,
        widget=Select2MultipleWidget,
    )
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local"
        })
    )

    class Meta:
        model = Project
        fields = ("name", "description", "deadline", "teams",)


class ProjectNameSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput({"placeholder": "Search by name"})
    )
