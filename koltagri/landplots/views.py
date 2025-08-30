from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.



class CultivatesView(TemplateView):
    template_name = 'cultivos.html'

class CultivatesDetailView(TemplateView):
    template_name = 'cultivate_detail.html'