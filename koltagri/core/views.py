from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.


class IndexView(TemplateView):
    template_name = "index.html"

class LoginView(TemplateView):
    template_name = "login.html"

class RegisterView(TemplateView):
    template_name = 'register.html'

class NotificationsView(TemplateView):
    template_name = 'notifications.html'

class ProfileView(TemplateView):
    template_name = 'profile.html'

class TeamView(TemplateView):
    template_name = 'team.html'

class LandsView(TemplateView):
    template_name = 'lands.html'

class PropertyView(TemplateView):
    template_name = 'property.html'