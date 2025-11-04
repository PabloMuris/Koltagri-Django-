from django.urls import path,re_path
from .views import TaskTemplateView,TaskDetailTemplateView,TaskboardTemplateView,TaskFormTemplateView
urlpatterns = [
    path("",TaskTemplateView.as_view(),name= "tasks"),
    path("tarefa/",TaskDetailTemplateView.as_view(),name= "task_detail"),
    path("nova-tarefa",TaskFormTemplateView.as_view(),name='task_form'),
]
