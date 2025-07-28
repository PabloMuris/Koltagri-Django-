from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import PlantSpecies,Cultivation,CultivationPlant
from ..permissions import IsSiteOwner
from .serializers import PlantSpeciesSerializer


class PlantViewSet(ModelViewSet):
    queryset = PlantSpecies.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PlantSpeciesSerializer

class CultivationViewSet(ModelViewSet):
    queryset = Cultivation.objects.all()
    permission_classes = [IsSiteOwner]
    serializer_class = PlantSpeciesSerializer

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class ClimateZoneViewSet(ReadOnlyModelViewSet):
    queryset = ClimateZone.objects.all()
    serializer_class = ClimateZoneSerializer
    permission_classes = [IsAuthenticated]