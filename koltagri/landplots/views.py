from django.shortcuts import render
from django.views.generic import TemplateView,ListView,DetailView,FormView,CreateView,UpdateView,DeleteView,View
# Create your views here
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from koltagri.landplots.models import CultivationPlant,PlantSpecies

from django.shortcuts import get_object_or_404
from .models import Site

from .forms import CultivationPlantForm

from .filters import CultivationPlantFilter

from django.urls import reverse_lazy
# views.py (atualize a classe CultivatedPlantsView)
from .filters import CultivationPlantFilter
from .models import Cultivation, ClimateZone

class CultivatedPlantsView(LoginRequiredMixin, FilterView):
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
        ).select_related(
            'plant_species',
            'cultivation',
            'cultivation__site',
        ).prefetch_related(
            'plant_species__climate_zones',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter o site_id da sessão
        site_id = self.request.session.get("selected_site_location")
        
        # Adicionar opções para os filtros
        if site_id:
            context['cultivation_options'] = Cultivation.objects.filter(site_id=site_id)
        else:
            context['cultivation_options'] = Cultivation.objects.none()
        
        context['climate_options'] = ClimateZone.objects.all()
        
        # Adicionar valor atual da busca, se existir
        context['current_search'] = self.request.GET.get('plant_species__name', '')
        
        return context

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

class CultivationPlantCreateView(CreateView):
    model = CultivationPlant
    form_class = CultivationPlantForm
    template_name = "landplots/cultivation_form.html"
    success_url = reverse_lazy("cultivated_plants")