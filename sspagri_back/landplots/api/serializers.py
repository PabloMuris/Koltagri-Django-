from rest_framework import serializers
from ..models import PlantSpecies

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



