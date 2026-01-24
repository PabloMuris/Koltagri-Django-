from django.shortcuts import render
from django.views.generic import TemplateView

from koltagri.core.mixins import SiteRequiredMixin

# Create your views here.

class ProfileView(SiteRequiredMixin, TemplateView):
    template_name = 'profile.html'

class SignupView(TemplateView):
    template_name = 'signup.html'