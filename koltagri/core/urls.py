from django.urls import path
from .views import IndexView, LoginView,RegisterView

urlpatterns = [
    path("",IndexView.as_view(),name='index'),
    path("login/",LoginView.as_view(),name='login'),
    path("register/",RegisterView.as_view(),name='register'),
]
