from django.urls import path, include
from .views import (
    CultivatedPlantsView, CultivatedPlantsDetailView, 
    CultivationPlantCreateView, CultivationPlantUpdateView, 
    CultivationPlantDeleteView,
    HarvestCultivationPlantListView, HarvestCultivationPlantCreateView,
    HarvestCultivationPlantUpdateView, HarvestCultivationPlantDeleteView
)

urlpatterns = [
    path("", CultivatedPlantsView.as_view(), name="cultivated_plants"),
    path("plantio/<int:pk>/", CultivatedPlantsDetailView.as_view(), name="cultivated_plants_detail"),
    path("novo-cultivo", CultivationPlantCreateView.as_view(), name="cultivation_form"),
    path("plantio/<int:pk>/editar", CultivationPlantUpdateView.as_view(), name='edit_cultivation_plant'),
    path("plantio/<int:pk>/delete", CultivationPlantDeleteView.as_view(), name='delete_cultivation_plant'),
    
    # Harvest URLs
    path("plantio/<int:cultivation_plant_pk>/colheitas/", 
         HarvestCultivationPlantListView.as_view(), 
         name='harvest_list'),
    path("plantio/<int:cultivation_plant_pk>/colheitas/nova/", 
         HarvestCultivationPlantCreateView.as_view(), 
         name='harvest_create'),
    path("plantio/<int:cultivation_plant_pk>/colheitas/<int:pk>/editar/", 
         HarvestCultivationPlantUpdateView.as_view(), 
         name='harvest_edit'),
    path("plantio/<int:cultivation_plant_pk>/colheitas/<int:pk>/excluir/", 
         HarvestCultivationPlantDeleteView.as_view(), 
         name='harvest_delete'),
]