from django.shortcuts import render
from django.views.generic import TemplateView,ListView,DetailView,FormView,CreateView,UpdateView,DeleteView
# Create your views here.

class CultivatedPlantsView(TemplateView):
    template_name = 'cultivated_plants.html'

class CultivatedPlantsDetailView(TemplateView):
    template_name = 'plant_detail.html'

class CultivationFormView(TemplateView):
    template_name = 'cultivation_form.html'

