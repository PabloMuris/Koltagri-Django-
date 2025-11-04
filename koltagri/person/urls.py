from django.urls import path

from .views import ProfileView

urlpatterns = [
    path("perfil", ProfileView.as_view(),name='profile')
]
