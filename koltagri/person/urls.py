from django.urls import path
from .views import ProfileView, SignupView, LogoutView

urlpatterns = [
    path("perfil", ProfileView.as_view(), name='profile'),
    path("sign-up", SignupView.as_view(), name='signup'),
    path("logout/", LogoutView.as_view(), name='logout'),
]