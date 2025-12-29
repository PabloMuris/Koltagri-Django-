from django import forms
from .models import Task

class TaskForm(forms.ModelForm):

    
    class Meta:
        model = Task
        fields = ["name", "description", "due_date", "priority"]
    
    def clean_priority(self):
        priority = self.cleaned_data.get('priority')
        if priority not in [0, 1, 2, 3]:
            raise forms.ValidationError("Prioridade inválida...")
        return priority
    