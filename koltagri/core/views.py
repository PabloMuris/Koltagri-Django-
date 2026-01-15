import os
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseNotAllowed,JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import TemplateView,View
from django.contrib.auth.mixins import LoginRequiredMixin

from django_filters.views import FilterView
# Create your views here.
from django.contrib.auth.models import Group
from .models import SiteInvite
from django_filters.views import FilterView

from koltagri.core.constants import ROLE_EMPLOYEE,ROLE_SITE_MANAGER
from koltagri.landplots.models import Site,SiteMembership

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect

from koltagri.tasks.models import Attachment

from django.contrib import messages

import json

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
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Busca o membro ou retorna None
        member = SiteMembership.objects.filter(user=user).first()
        
        # Atribui True se o member existir E o role for o correto, senão False
        context['is_manager'] = member is not None and member.role == ROLE_SITE_MANAGER
        
        return context


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
        query = super().get_queryset()
        
        return query.filter(members=self.request.user)
    

class AddAttachmentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pass

class AcceptInviteView(LoginRequiredMixin, View):

    def get(self, request, token):
        invite = get_object_or_404(SiteInvite, token=token)

        if not invite.is_valid():
            messages.error(request, "Convite inválido ou expirado.")
            return redirect("select_site")

        # já é membro?
        if SiteMembership.objects.filter(
            site=invite.site,
            user=request.user
        ).exists():
            messages.info(request, "Você já faz parte desse site.")
            return redirect("select_site")

        # ✅ cria vínculo com o Group do convite
        SiteMembership.objects.create(
            site=invite.site,
            user=request.user,
            role=invite.role
        )

        invite.is_used = True
        invite.save(update_fields=["is_used"])

        # opcional: setar site na sessão
        request.session["selected_site_location"] = invite.site.id
        request.session["selected_site_name"] = invite.site.name

        messages.success(
            request,
            f"Você entrou no site {invite.site.name} como {invite.role.name}."
        )

        return redirect("index")



# core/views.py







class CreateInviteView(LoginRequiredMixin, View):

    def post(self, request, site_id):
        site = get_object_or_404(Site, id=site_id)

        # 🔐 permissão: só Site Manager pode convidar
        manager_group = Group.objects.get(name="Site Manager")

        if not SiteMembership.objects.filter(
            site=site,
            user=request.user,
            role=manager_group
        ).exists():
            return JsonResponse({"error": "Sem permissão"}, status=403)

        data = json.loads(request.body or "{}")

        # 🎭 role do convite (nome do Group)
        role_name = data.get("role", "Employee")
        role = get_object_or_404(Group, name=role_name)

        # ⏳ expiração
        expires_days = int(data.get("expires", 7))
        expires_at = (
            timezone.now() + timedelta(days=expires_days)
            if expires_days > 0
            else None
        )

        invite = SiteInvite.objects.create(
            site=site,
            invited_by=request.user,
            role=role,
            expires_at=expires_at
        )

        invite_link = request.build_absolute_uri(
            reverse("accept-invite", args=[invite.token])
        )

        return JsonResponse({
            "invite_link": invite_link
        })
