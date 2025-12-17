from django.urls import path,re_path
from .views import CultivatedPlantsView,CultivatedPlantsDetailView,CultivationFormView
urlpatterns = [
    path("",CultivatedPlantsView.as_view(),name="cultivated_plants"),
    path("planta/<int:pk>/",CultivatedPlantsDetailView.as_view(),name="cultivated_plants_detail"),
    path("novo-cultivo",CultivationFormView.as_view(),name="cultivation_form"),
]
