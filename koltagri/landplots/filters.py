# filters.py
import django_filters
from django import forms
from .models import CultivationPlant, Cultivation, PlantSpecies, ClimateZone

class CultivationPlantFilter(django_filters.FilterSet):
    # Filtro por nome da espécie
    plant_species__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nome da planta',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nome...'})
    )
    
    # Filtro por área de cultivo
    cultivation = django_filters.ModelChoiceFilter(
        queryset=Cultivation.objects.none(),  # Será sobrescrito no __init__
        label='Área de cultivo',
        empty_label='Todas as áreas'
    )
    
    # Filtro por clima
    plant_species__climate_zones = django_filters.ModelChoiceFilter(
        queryset=ClimateZone.objects.all(),
        label='Clima',
        empty_label='Todos os climas'
    )
    
    class Meta:
        model = CultivationPlant
        fields = ['plant_species__name', 'cultivation', 'plant_species__climate_zones']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se houver um request no contexto (FilterView fornece), podemos filtrar as áreas pelo site
        request = kwargs.get('request', None)
        if request and hasattr(request, 'session'):
            site_id = request.session.get("selected_site_location")
            if site_id:
                # Filtrar apenas as áreas do site selecionado
                self.filters['cultivation'].queryset = Cultivation.objects.filter(site_id=site_id)