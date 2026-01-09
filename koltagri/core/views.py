import os
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseNotAllowed
from django.shortcuts import render
from django.views.generic import TemplateView,View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

from django_filters.views import FilterView


from koltagri.landplots.models import Site

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect

class IndexView(LoginRequiredMixin,TemplateView):
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



@login_required
def select_site_location(request,site_id):

    selected_site = get_object_or_404(Site, id=site_id, members=request.user)

    if not selected_site:
        return redirect('select_site')

    request.session['selected_site_location'] = selected_site.id

    request.session['selected_site_name'] = selected_site.name

    request.session.modified = True

    print(request.session['selected_site_location'])
    return redirect('index')


class SelectSiteView(LoginRequiredMixin,FilterView):
    template_name = 'select_site.html'
    model = Site
    context_object_name = 'sites'
    filterset_fields = ["name"]

    def get_queryset(self):
        return Site.objects.filter(members=self.request.user)