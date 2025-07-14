from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import PlantSpecies,Cultivation,CultivationPlant
from ..permissions import IsSiteOwner
from .serializers import PlantSpeciesSerializer


class PlantViewSet(ModelViewSet):
    queryset = PlantSpecies.objects.all()
    permission_classes = [IsSiteOwner]
    serializer_class = PlantSpeciesSerializer

class CultivationViewSet(ModelViewSet):
    queryset = Cultivation.objects.all()
    permission_classes = [IsSiteOwner]
    serializer_class = PlantSpeciesSerializer