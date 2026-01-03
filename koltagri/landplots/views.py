from django.shortcuts import render
from django.views.generic import TemplateView,ListView,DetailView,FormView,CreateView,UpdateView,DeleteView
# Create your views here
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from koltagri.landplots.models import CultivationPlant,PlantSpecies

from django.shortcuts import get_object_or_404
from .models import Site

from .filters import CultivationPlantFilter


class CultivatedPlantsView(LoginRequiredMixin,FilterView):
    model = CultivationPlant
    template_name = 'cultivated_plants.html'
    filterset_class = CultivationPlantFilter
    context_object_name = 'cultivated_plants'
    paginate_by = 10


    def get_queryset(self):
        site_id = self.request.session.get("selected_site_location")

        if not site_id:
            return CultivationPlant.objects.none()

        return CultivationPlant.objects.filter(
            cultivation__site_id=site_id
        )


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


