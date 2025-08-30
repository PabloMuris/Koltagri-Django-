from django.urls import path,re_path
from .views import CultivatesView,CultivatesDetailView
urlpatterns = [
    path('',CultivatesView.as_view(),name='cultivates'),
    path('detalhes',CultivatesDetailView.as_view(),name='cultivates_detail'),
    path('site')
]
