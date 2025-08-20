from django.urls import path,re_path
from .views import CultivatesView
urlpatterns = [
    path('',CultivatesView.as_view(),name='cultivates')
]
