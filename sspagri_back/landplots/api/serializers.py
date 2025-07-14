from rest_framework import serializers
from ..models import PlantSpecies,Cultivation,CultivationPlant

class PlantSpeciesSerializer(serializers.ModelSerializer):

     class Meta:
        model = PlantSpecies
        fields = [
            'id',
            'name',
            'life_cycle',
            'germination',
            'flowering',
            'fructification',
            'precipitation_needs',
            'climate_zones',
        ]

class CultivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cultivation
        fields = [
            'id',
            'name',
            'life_cycle',
            'germination',
            'flowering',
            'fructification',
            'precipitation_needs',
            'climate_zones',
        ]

class CultivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CultivationPlant
        fields = [
            'id',
            'name',
            'life_cycle',
            'germination',
            'flowering',
            'fructification',
            'precipitation_needs',
            'climate_zones',
        ]

