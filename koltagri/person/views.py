from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class ProfileView(TemplateView):
    template_name = 'profile.html'

class SignupView(TemplateView):
    template_name = 'signup.html'