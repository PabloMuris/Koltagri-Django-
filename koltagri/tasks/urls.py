from django.urls import path,re_path
from .views import TaskTemplateView,TaskDetailTemplateView,TaskboardTemplateView
urlpatterns = [
    path("",TaskTemplateView.as_view(),name= "tasks"),
    path("tasks_list/",TaskDetailTemplateView.as_view(),name= "task_detail"),
    path("tasks/", TaskboardTemplateView.as_view(),name="task_board")
]
