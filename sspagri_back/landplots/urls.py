from django.urls import path
from rest_framework.routers import SimpleRouter
from .api.views import PlantViewSet,ClimateZoneViewSet,TaskViewSet

router = SimpleRouter()

router.register('plants', PlantViewSet)
router.register('climatezone',ClimateZoneViewSet)
router.register('tasks',TaskViewSet)




urlpatterns = [
] + router.urls

