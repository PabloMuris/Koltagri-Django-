from django.urls import path,re_path
from .views import CultivatedPlantsView,CultivatedPlantsDetailView,CultivationPlantCreateView,CultivationPlantUpdateView,CultivationPlantDeleteView
urlpatterns = [
    path("",CultivatedPlantsView.as_view(),name="cultivated_plants"),
    path("plantio/<int:pk>/",CultivatedPlantsDetailView.as_view(),name="cultivated_plants_detail"),
    path("novo-cultivo",CultivationPlantCreateView.as_view(),name="cultivation_form"),
    path("plantio/<int:pk>/editar",CultivationPlantUpdateView.as_view(),name='edit_cultivation_plant'),
    path("plantio/<int:pk>/delete",CultivationPlantDeleteView.as_view(),name='delete_cultivation_plant'),
]
