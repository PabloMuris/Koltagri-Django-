from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import (
    ClimateZone,
    PlantSpecies,
    Site,
    Cultivation,
    CultivationPlant,
    SiteMembership,
    Task,
)
from django.contrib.auth.models import Group
User = get_user_model()

from sspagri_back.core.constants import (
    ROLE_SITE_OWNER,
            ROLE_SITE_MANAGER,
            ROLE_STUDY_TEAM,
            ROLE_STUDY_MANAGER,
)

class ClimateZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateZone
        fields = ['code']

        
class PlantSpeciesSerializer(serializers.ModelSerializer):
     
     climate_zones = serializers.SlugRelatedField(
        many=True,                 
        slug_field='code',         
        queryset=ClimateZone.objects.all()
    )
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




class SiteSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(
        queryset=Site._meta.get_field('country').related_model.objects.all(),
        allow_null=True,
        required=False
    )
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'country',
            'number', 'timezone',
            'created_at', 'updated_at',
            'members',
        ]


class CultivationSerializer(serializers.ModelSerializer):
    site = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.all()
    )

    class Meta:
        model = Cultivation
        fields = [
            'id', 'name', 'site',
            'quantity',
            'is_deleted', 'deleted_at',
        ]


class CultivationPlantSerializer(serializers.ModelSerializer):
    cultivation = serializers.PrimaryKeyRelatedField(
        queryset=Cultivation.objects.all()
    )
    plant_species = serializers.PrimaryKeyRelatedField(
        queryset=PlantSpecies.objects.all()
    )

    class Meta:
        model = CultivationPlant
        fields = [
            'id', 'cultivation', 'plant_species',
            'planting_day', 'harvest_day', 'count',
            'is_deleted', 'deleted_at',
        ]

    def validate(self, data):
        """
        Garante que harvest_day >= planting_day
        """
        if data['harvest_day'] < data['planting_day']:
            raise serializers.ValidationError({
                'harvest_day': 'A data de colheita não pode ser anterior à de plantio.'
            })
        return data


class SiteMembershipSerializer(serializers.ModelSerializer):
    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = SiteMembership
        fields = [
            'id', 'site', 'user', 'role',
            'created_at', 'updated_at',
        ]

    def validate_role(self, role):
        allowed = {
            ROLE_SITE_OWNER,
            ROLE_SITE_MANAGER,
            ROLE_STUDY_TEAM,
            ROLE_STUDY_MANAGER,
        }
        if role.name not in allowed:
            raise serializers.ValidationError(
                f"O grupo “{role.name}” não é um papel permitido para SiteMembership."
            )
        return role


class TaskSerializer(serializers.ModelSerializer):
    cultivation_plant = serializers.SlugRelatedField(
        many=True,
        queryset=CultivationPlant.objects.all(),
        slug_field='uuid'
    )

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description',
            'cultivation_plant', 'start_in', 'end_in',
            'created_at', 'updated_at',
        ]

    def validate(self, data):
        if data['end_in'] < data['start_in']:
            raise serializers.ValidationError({
                'end_in': 'A data de término não pode ser anterior ao início.'
            })
        return data

    def create(self, validated_data):
        plants = validated_data.pop('cultivation_plant')  # Corrigido
        task = Task.objects.create(**validated_data)
        task.cultivation_plant.set(plants)  # Corrigido
        return task

    def update(self, instance, validated_data):
        plants = validated_data.pop('cultivation_plant', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if plants is not None:
            instance.cultivation_plant.set(plants)
        return instance