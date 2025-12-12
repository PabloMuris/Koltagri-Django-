from django import forms
from django.forms import inlineformset_factory
from .models import Task, Attachment


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "cultivation_plant",
            "supplies",
            "start_in",
            "end_in",
            "user",
            "priority",
        ]
        widgets = {
            "start_in": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_in": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "cultivation_plant": forms.SelectMultiple(attrs={"class": "select"}),
            "supplies": forms.SelectMultiple(attrs={"class": "select"}),
        }


AttachmentFormSet = inlineformset_factory(
    Task,
    Attachment,
    fields=("file", "name", "type"),
    extra=1,
    can_delete=True,
)
