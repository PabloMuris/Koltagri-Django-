# filters.py
import django_filters
from django_filters import CharFilter, ModelMultipleChoiceFilter, DateFromToRangeFilter, ChoiceFilter
from .models import CultivationPlant, ClimateZone, PlantSpecies

class CultivationPlantFilter(django_filters.FilterSet):

    # nome da espécie
    name = CharFilter(
        field_name="plant_species__name",
        lookup_expr="icontains",
        label="Espécie"
    )

    # clima (Köppen) - M2M
    climate = ModelMultipleChoiceFilter(
        field_name="plant_species__climate_zones",
        queryset=ClimateZone.objects.all(),
        label="Zona climática"
    )

    # 🌞 luminosidade (3 opções apenas)
    luminosity = ChoiceFilter(
        field_name="plant_species__luminosity_needs",
        choices=PlantSpecies.LuminosityNeeds.choices,
        label="Luminosidade"
    )

    # data de criação
    created = DateFromToRangeFilter(
        field_name="created_at",
        label="Criado em"
    )

    class Meta:
        model = CultivationPlant
        fields = ["name", "climate", "luminosity", "created"]
