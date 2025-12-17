from django.urls import path,re_path

namespace = "tasks"

from .views import TaskTemplateView,TaskDetailTemplateView,TaskboardTemplateView,TaskParticipantTemplateView,TaskDocsTemplateView,fetch_plant_species,TaskCreateUpdateView
urlpatterns = [
    path("",TaskTemplateView.as_view(),name= "tasks"),
    path("tarefa/<int:pk>/",TaskDetailTemplateView.as_view(),name= "task_detail"),
    path("nova-tarefa",TaskCreateUpdateView.as_view(),name='task_form'),
    path("tarefa/<int:pk>/editar",TaskCreateUpdateView.as_view(),name='task_form'),
    path("tarefa/participants",TaskParticipantTemplateView.as_view(),name="task_participant"),
    path("tarefa/anexos", TaskDocsTemplateView.as_view(),name="docs"),
    path("plantas-especies/",fetch_plant_species,name="fetch_plant_species"),
]
