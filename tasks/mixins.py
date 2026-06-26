from django import forms
from django.utils import timezone


class DeadlineValidationMixin:
    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline is None:
            return deadline

        original_deadline = getattr(self.instance, "deadline", None)
        deadline_changed = original_deadline != deadline

        if deadline_changed and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past")
        return deadline
