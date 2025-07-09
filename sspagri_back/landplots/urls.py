from django.urls import path
from rest_framework.routers import SimpleRouter
from .api.views import PlantViewSet

router = SimpleRouter()

router.register('plants', PlantViewSet)




urlpatterns = [
    
] + router.urls

