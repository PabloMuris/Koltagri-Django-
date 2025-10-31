from django.urls import path,re_path
from .views import TaskTemplateView,TaskDetailTemplateView
urlpatterns = [
    path("",TaskTemplateView.as_view(),name= "tasks"),
    path("tasks/",TaskDetailTemplateView.as_view(),name= "task_detail"),
]
