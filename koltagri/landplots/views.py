from django.shortcuts import render
from django.views.generic import TemplateView,ListView,DetailView,FormView,CreateView,UpdateView,DeleteView
# Create your views here
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from koltagri.landplots.models import CultivationPlant,PlantSpecies


from .filters import CultivationPlantFilter


class CultivatedPlantsView(LoginRequiredMixin,FilterView):
    template_name = 'cultivated_plants.html'
    filterset_class = CultivationPlantFilter
    queryset = CultivationPlant.objects.all()
    context_object_name = 'cultivated_plants'
    paginate_by = 10


class CultivatedPlantsDetailView(LoginRequiredMixin, DetailView):
    model = CultivationPlant
    template_name = 'plant_detail.html'
    context_object_name = 'plant'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                'plant_species',
                'cultivation',
                'cultivation__site',
            )
            .prefetch_related(
                'plant_species__climate_zones',
                'events',  # PlantingEvent
            )
        )

class CultivationFormView(LoginRequiredMixin,TemplateView):
    template_name = 'cultivation_form.html'


