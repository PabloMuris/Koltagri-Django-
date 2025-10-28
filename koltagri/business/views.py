from django.shortcuts import render
from django.views.generic import TemplateView   
# Create your views here.

class BusinessDashboardView(TemplateView):
    template_name = 'business.html'

class PlanningView(TemplateView):
    template_name = 'planning_form.html'

class StatisticsView(TemplateView):
    template_name = 'statistics.html'