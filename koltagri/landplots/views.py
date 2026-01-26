from django.shortcuts import render
from django.views.generic import TemplateView,ListView,DetailView,FormView,CreateView,UpdateView,DeleteView,View
# Create your views here
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from koltagri.landplots.models import CultivationPlant,PlantSpecies,HarvestCultivationPlant

from django.shortcuts import get_object_or_404
from .models import Site
from django.utils.translation import gettext_lazy as _
from .forms import CultivationPlantForm,HarvestCultivationPlantForm

from .filters import CultivationPlantFilter
from django.db.models import Sum
from django.urls import reverse_lazy
# views.py (atualize a classe CultivatedPlantsView)
from .filters import CultivationPlantFilter
from .models import Cultivation, ClimateZone

from django.shortcuts import redirect
from django.contrib import messages


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from koltagri.core.mixins import IsManagerOrTechnicalAssistanceMixin,IsStaffMixin,IsManagerMixin,SiteRequiredMixin

class CultivatedPlantsView(SiteRequiredMixin, FilterView):
    model = CultivationPlant
    template_name = 'landplots/cultivated_plants.html'
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
    template_name = 'landplots/plant_detail.html'
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cultivation_plant_pk'] = self.kwargs['pk']
        return context

class CultivationPlantCreateView(IsManagerOrTechnicalAssistanceMixin, CreateView):
    model = CultivationPlant
    form_class = CultivationPlantForm
    template_name = "landplots/cultivation_form.html"
    success_url = reverse_lazy("cultivated_plants")


class CultivationPlantUpdateView(IsManagerOrTechnicalAssistanceMixin, UpdateView):
    model = CultivationPlant
    form_class = CultivationPlantForm
    template_name = "landplots/cultivation_form.html"
    success_url = reverse_lazy("cultivated_plants")
    
    def get_queryset(self):
        site_id = self.request.session.get("selected_site_location")
        if site_id:
            return CultivationPlant.objects.filter(
                cultivation__site_id=site_id
            )
        return CultivationPlant.objects.none()

class CultivationPlantDeleteView(IsManagerOrTechnicalAssistanceMixin, View):
    def post(self, request, *args, **kwargs):
        # Recupera o objeto pelo ID (pk) vindo da URL
        plant = get_object_or_404(CultivationPlant, id=kwargs.get("pk"))
        
        # Verificar se a planta pertence ao site atual do usuário
        site_id = request.session.get("selected_site_location")
        if site_id and plant.cultivation.site_id != int(site_id):
            messages.error(request, "Você não tem permissão para excluir esta planta.")
            return redirect("cultivated_plants")
        
        # Executa a exclusão
        plant.delete()
        
        # Mensagem de sucesso
        messages.success(request, "Planta excluída com sucesso!")
        
        # Redireciona para a página desejada (ex: lista de plantios)
        return redirect("cultivated_plants")
    

class HarvestCultivationPlantListView(IsManagerOrTechnicalAssistanceMixin, ListView):
    model = HarvestCultivationPlant
    template_name = 'landplots/harvest_list.html'
    context_object_name = 'harvests'
    paginate_by = 10
    
    def get_queryset(self):
        cultivation_plant_pk = self.kwargs['cultivation_plant_pk']
        site_id = self.request.session.get("selected_site_location")
        
        # Verificar se o cultivation_plant pertence ao site
        cultivation_plant = get_object_or_404(
            CultivationPlant.objects.filter(
                cultivation__site_id=site_id
            ),
            pk=cultivation_plant_pk
        )
        
        return HarvestCultivationPlant.objects.filter(
            cultivation_plant=cultivation_plant
        ).select_related('cultivation_plant').order_by('-harvest_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cultivation_plant_pk = self.kwargs['cultivation_plant_pk']
        site_id = self.request.session.get("selected_site_location")
        
        cultivation_plant = get_object_or_404(
            CultivationPlant.objects.filter(
                cultivation__site_id=site_id
            ),
            pk=cultivation_plant_pk
        )
        
        # Estatísticas
        harvests = HarvestCultivationPlant.objects.filter(
            cultivation_plant=cultivation_plant
        )
        
        total_quantity = harvests.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Converter para a unidade principal (kg) para exibição
        context['cultivation_plant'] = cultivation_plant
        context['total_harvests'] = harvests.count()
        context['total_quantity'] = total_quantity
        context['cultivation_plant_pk'] = cultivation_plant_pk
        
        return context

class HarvestCultivationPlantCreateView(IsManagerOrTechnicalAssistanceMixin, CreateView):
    model = HarvestCultivationPlant
    form_class = HarvestCultivationPlantForm
    template_name = 'landplots/harvest_form.html'
    
    def get_cultivation_plant(self):
        cultivation_plant_pk = self.kwargs['cultivation_plant_pk']
        site_id = self.request.session.get("selected_site_location")
        
        cultivation_plant = get_object_or_404(
            CultivationPlant.objects.filter(
                cultivation__site_id=site_id
            ),
            pk=cultivation_plant_pk
        )
        return cultivation_plant
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Definir o cultivation_plant inicial
        form.instance.cultivation_plant = self.get_cultivation_plant()
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cultivation_plant'] = self.get_cultivation_plant()
        context['cultivation_plant_pk'] = self.kwargs['cultivation_plant_pk']
        context['is_create'] = True
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Colheita registrada com sucesso!')
        return reverse_lazy('harvest_list', kwargs={
            'cultivation_plant_pk': self.kwargs['cultivation_plant_pk']
        })

class HarvestCultivationPlantUpdateView(IsManagerOrTechnicalAssistanceMixin, UpdateView):
    model = HarvestCultivationPlant
    form_class = HarvestCultivationPlantForm
    template_name = 'landplots/harvest_form.html'
    
    def get_queryset(self):
        site_id = self.request.session.get("selected_site_location")
        cultivation_plant_pk = self.kwargs['cultivation_plant_pk']
        
        # Filtrar apenas colheitas do cultivation_plant correto e do site
        return HarvestCultivationPlant.objects.filter(
            cultivation_plant__cultivation__site_id=site_id,
            cultivation_plant_id=cultivation_plant_pk
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cultivation_plant'] = self.object.cultivation_plant
        context['cultivation_plant_pk'] = self.kwargs['cultivation_plant_pk']
        context['is_create'] = False
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Colheita atualizada com sucesso!')
        return reverse_lazy('harvest_list', kwargs={
            'cultivation_plant_pk': self.kwargs['cultivation_plant_pk']
        })

class HarvestCultivationPlantDeleteView(IsManagerOrTechnicalAssistanceMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        cultivation_plant_pk = kwargs['cultivation_plant_pk']
        harvest_pk = kwargs['pk']
        site_id = request.session.get("selected_site_location")
        
        try:
            # Verificar se a colheita pertence ao cultivation_plant e ao site
            harvest = HarvestCultivationPlant.objects.get(
                pk=harvest_pk,
                cultivation_plant_id=cultivation_plant_pk,
                cultivation_plant__cultivation__site_id=site_id
            )
            
            # Salvar informações para mensagem
            harvest_date = harvest.harvest_date
            harvest_quantity = harvest.quantity
            
            # Excluir a colheita
            harvest.delete()
            
            messages.success(request, f'Colheita de {harvest_date.strftime("%d/%m/%Y")} excluída com sucesso!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Colheita de {harvest_date.strftime("%d/%m/%Y")} excluída com sucesso!'
                })
            
            return redirect('harvest_list', cultivation_plant_pk=cultivation_plant_pk)
            
        except HarvestCultivationPlant.DoesNotExist:
            messages.error(request, 'Colheita não encontrada ou você não tem permissão para excluí-la.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Colheita não encontrada.'
                }, status=404)
            
            return redirect('harvest_list', cultivation_plant_pk=cultivation_plant_pk)
        

