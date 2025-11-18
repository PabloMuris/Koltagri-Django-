from django.urls import path,re_path

namespace = "tasks"

from .views import TaskTemplateView,TaskDetailTemplateView,TaskboardTemplateView,TaskFormTemplateView,TaskParticipantTemplateView,TaskDocsTemplateView
urlpatterns = [
    path("",TaskTemplateView.as_view(),name= "tasks"),
    path("tarefa/",TaskDetailTemplateView.as_view(),name= "task_detail"),
    path("nova-tarefa",TaskFormTemplateView.as_view(),name='task_form'),
    path("tarefa/participants",TaskParticipantTemplateView.as_view(),name="task_participant"),
    path("tarefa/anexos", TaskDocsTemplateView.as_view(),name="docs")
]
