import os
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseNotAllowed,JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import TemplateView,View
from django.contrib.auth.mixins import LoginRequiredMixin

from django_filters.views import FilterView
# Create your views here.

from .models import SiteInvite
from django_filters.views import FilterView

from koltagri.core.constants import ROLE_EMPLOYEE,ROLE_SITE_MANAGER
from koltagri.landplots.models import Site,SiteMembership

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect

from koltagri.tasks.models import Attachment

from django.contrib import messages

from django.utils import timezone
from datetime import timedelta

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

class TeamView(LoginRequiredMixin, FilterView):
    template_name = 'team.html'
    model = SiteMembership
    context_object_name = "people"



    def get_queryset(self):
        original_query = super().get_queryset()
        query = original_query.filter(
            site= self.request.session["selected_site_location"]
        )
        return query

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
    filterset_fields = {
        "name": ["icontains"],
    }
    paginate_by = 10

    def get_queryset(self):
        return Site.objects.filter(members=self.request.user)
    

class AddAttachmentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pass

class AcceptInviteView(LoginRequiredMixin, View):

    def get(self, request, token):
        invite = get_object_or_404(SiteInvite, token=token)

        if not invite.is_valid():
            messages.error(request, "Convite inválido ou expirado.")
            return redirect("select_site")

        # Já é membro?
        if SiteMembership.objects.filter(
            user=request.user,
            site=invite.site
        ).exists():
            messages.info(request, "Você já faz parte desse site.")
            return redirect("select_site")

        # Cria o vínculo
        SiteMembership.objects.create(
            user=request.user,
            site=invite.site,
            role=ROLE_EMPLOYEE
        )

        invite.is_used = True
        invite.save()

        # Seta o site na sessão
        request.session["site_id"] = invite.site.id

        messages.success(
            request,
            f"Você entrou no site {invite.site.name} como funcionário."
        )

        return redirect("dashboard")


class CreateInviteView(LoginRequiredMixin, View):

    def post(self, request, site_id):
        site = get_object_or_404(Site, id=site_id)

        # Verifica se o usuário é dono / manager
        if not site.memberships.filter(
            user=request.user,
            role=ROLE_SITE_MANAGER
        ).exists():
            return JsonResponse({"error": "Sem permissão"}, status=403)

        invite = SiteInvite.objects.create(
            site=site,
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=7)
        )

        invite_link = request.build_absolute_uri(
            reverse("sites:accept-invite", args=[invite.token])
        )

        return JsonResponse({
            "invite_link": invite_link
        })