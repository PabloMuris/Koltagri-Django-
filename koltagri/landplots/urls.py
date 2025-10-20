from django.urls import path,re_path
from .views import CultivatedPlantsView
urlpatterns = [
    path("",CultivatedPlantsView.as_view(),name="cultivated_plants"),
]
