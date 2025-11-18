from django.shortcuts import render
from django.views.generic import ListView,TemplateView

from .models import Task

# Create your views here.

class TaskTemplateView(ListView):
    template_name = "tasks.html"
    context_object_name = "tasks"
    model = Task  


class TaskDetailTemplateView(ListView):
    template_name = "tasks_detail.html"
    context_object_name = "task_d"
    model = Task  

class TaskboardTemplateView(ListView):
    template_name = "task_board.html"
    context_object_name = "task_d"
    model = Task 

class TaskFormTemplateView(TemplateView):
    template_name = "task_form.html"

class TaskParticipantTemplateView(TemplateView):
    template_name = "task_team.html"

class TaskDocsTemplateView(TemplateView):
    template_name = "task_detail_docs.html"