from django.urls import path,re_path
from .views import CultivatedPlantsView,CultivatedPlantsDetailView
urlpatterns = [
    path("",CultivatedPlantsView.as_view(),name="cultivated_plants"),
    path("planta",CultivatedPlantsDetailView.as_view(),name="cultivated_plants_detail"),
]
