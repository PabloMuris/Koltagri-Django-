from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class CultivatedPlantsView(TemplateView):
    template_name = 'cultivated_plants.html'