from rest_framework.viewsets import GenericViewSet,ModelViewSet,ReadOnlyModelViewSet
from rest_framework.mixins import CreateModelMixin,UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from ..models import PlantSpecies,Cultivation,CultivationPlant,Task,ClimateZone
from ..permissions import IsSiteOwner
from .serializers import PlantSpeciesSerializer,TaskSerializer,ClimateZoneSerializer


class PlantViewSet(ModelViewSet):
    queryset = PlantSpecies.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PlantSpeciesSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class ClimateZoneViewSet(ReadOnlyModelViewSet):
    queryset = ClimateZone.objects.all()
    serializer_class = ClimateZoneSerializer
    permission_classes = [IsAuthenticated]
