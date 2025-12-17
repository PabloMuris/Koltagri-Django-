from django import forms
from django.forms import inlineformset_factory
from .models import Task, Attachment


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "due_date",
            "user",
            "priority",
        ]
        widgets = {
           
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),

        }



