from django.urls import path,re_path

namespace = "tasks"

from .views import (
    TaskAttachmentsTemplateView, 
    TaskTemplateView,
    TaskDetailTemplateView,
    TaskboardTemplateView,
    TaskParticipantTemplateView,
    TaskDocsTemplateView,
    fetch_plant_species,
    TaskCreateUpdateView,
    conclude_task,
    DownloadFileView
)
urlpatterns = [
    path("",TaskTemplateView.as_view(),name= "tasks"),
    path("tarefa/<int:pk>/",TaskDetailTemplateView.as_view(),name= "task_detail"),
    path("nova-tarefa",TaskCreateUpdateView.as_view(),name='task_form'),
    path("tarefa/<int:pk>/editar",TaskCreateUpdateView.as_view(),name='task_form'),
    path("tarefa/<int:pk>/participantes",TaskParticipantTemplateView.as_view(),name="task_participant"),
    path("plantas-especies/",fetch_plant_species,name="fetch_plant_species"),
    path("tarefa/<int:task_pk>/participante/<int:user_pk>/anexos", TaskAttachmentsTemplateView.as_view(),name="task_attachments"),
    path("concluir-tarefa/<int:pk>/", conclude_task, name="conclude_task"),
    path("download/<int:pk>/", DownloadFileView.as_view(), name="download_attch")

]