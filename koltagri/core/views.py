import os
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseNotAllowed,JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import TemplateView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

from django_filters.views import FilterView
# Create your views here.
from django.contrib.auth.models import Group
from .models import SiteInvite
from django_filters.views import FilterView

from koltagri.core.constants import ROLE_EMPLOYEE,ROLE_SITE_MANAGER
from koltagri.landplots.models import Site,SiteMembership,Cultivation

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect

from koltagri.tasks.models import Attachment

from django.contrib import messages

import json

from django.utils import timezone
from datetime import timedelta

from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse
from .forms import CustomUserCreationForm, UserInformationForm,SiteForm,CultivationForm
from koltagri.person.models import UserInformation
from .models import Country

from .mixins import SiteRequiredMixin
class IndexView(SiteRequiredMixin,TemplateView):
    template_name = "index.html"

from django.contrib.auth import authenticate, login
from .forms import LoginForm  # Importe o novo formulário

from django.contrib.auth import logout
class LoginView(View):
    template_name = "core/login.html"
    
    def get(self, request, *args, **kwargs):
        # Se já estiver autenticado, redireciona
        if request.user.is_authenticated:
            return redirect('index')
        
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            
            # Faz login do usuário
            login(request, user)
            
            # Verifica se o usuário tem algum site para selecionar
            user_sites = Site.objects.filter(members=user)
            
            if user_sites.count() == 1:
                # Se tiver apenas um site, seleciona automaticamente
                site = user_sites.first()
                request.session['selected_site_location'] = site.id
                request.session['selected_site_name'] = site.name
                messages.success(request, f"Bem-vindo, {user.first_name}!")
                return redirect('index')
            elif user_sites.exists():
                # Se tiver múltiplos sites, redireciona para seleção
                messages.success(request, f"Bem-vindo de volta, {user.first_name}!")
                return redirect('select_site')
            else:
                # Se não tiver sites, redireciona para criar um
                messages.info(request, "Você não possui propriedades. Cadastre sua primeira propriedade.")
                return redirect('create_site')
        
        # Se o formulário for inválido, retorna para a página de login com erros
        return render(request, self.template_name, {'form': form})

class NotificationsView(TemplateView):
    template_name = 'notifications.html'

# Em core/views.py, substitua a view ProfileView atual por esta:

from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from koltagri.person.forms import UserProfileForm
from koltagri.person.models import UserInformation
from koltagri.core.models import Country

class ProfileView( SiteRequiredMixin, FormView):
    template_name = 'profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Obtém ou cria o UserInformation para o usuário atual
        user_info, created = UserInformation.objects.get_or_create(
            user=self.request.user,
            defaults={
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'country': Country.objects.first() if Country.objects.exists() else None
            }
        )
        kwargs['user'] = self.request.user
        kwargs['instance'] = user_info
        return kwargs

    def form_valid(self, form):
        try:
            form.save()
            messages.success(self.request, 'Perfil atualizado com sucesso!')
        except Exception as e:
            messages.error(self.request, f'Erro ao atualizar perfil: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o user_info ao contexto para o template
        user_info, created = UserInformation.objects.get_or_create(
            user=self.request.user,
            defaults={
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'country': Country.objects.first() if Country.objects.exists() else None
            }
        )
        context['user_info'] = user_info
        context['has_profile_picture'] = bool(user_info.profile_picture)
        return context

class TeamView(LoginRequiredMixin, FilterView):
    template_name = 'team.html'
    model = SiteMembership
    context_object_name = "people"
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            
            # 1. Buscamos o membro filtrando pelo usuário E pelo site atual
            # (Assumi que 'self.object' nesta view seja o Site ou algo que tenha ligação com ele)
            member = SiteMembership.objects.filter(
                user=user, 
                site=self.request.session['selected_site_location'] # Ou self.object, dependendo da sua View
            ).first()

            # 2. Verificamos se o membro existe e se o NOME da role é o que queremos
            # Não precisamos buscar o objeto Group separadamente se já temos o nome na constante
            context['is_manager'] = member is not None and member.role.name == ROLE_SITE_MANAGER
        else:
            context['is_manager'] = False

        print(context['is_manager'])
        return context


    def get_queryset(self):
        original_query = super().get_queryset()
        query = original_query.filter(
            site= self.request.session["selected_site_location"]
        )
        return query

class LandsView(LoginRequiredMixin,FilterView):
    template_name = 'lands.html'
    model = Cultivation
    context_object_name = 'cultivations'
    paginate_by = 7

    def get_queryset(self):
        original_query = super().get_queryset()
        query = original_query.filter(
            site=self.request.session["selected_site_location"]
        )
        return query

class PropertyView(TemplateView):
    template_name = 'property.html'



@login_required
def select_site_location(request,site_id):

    selected_site = get_object_or_404(Site, id=site_id, members=request.user)

    if not selected_site:
        return HttpResponseNotFound

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
        
        group = Group.objects.filter(name=invite.role).first()

        # ✅ cria vínculo com o Group do convite
        SiteMembership.objects.create(
            site=invite.site,
            user=request.user,
            role=group
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


# views.py - Adicione esta view


# koltagri/core/views.py
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.utils import timezone

from koltagri.users.models import User
from koltagri.person.models import UserInformation
from koltagri.core.models import Country, State, City
from .forms import CustomUserCreationForm, UserInformationForm

class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')  # Ou a URL que você quiser
    
    def get(self, request, *args, **kwargs):
        # Se já estiver autenticado, redireciona
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_info_form' not in context:
            context['user_info_form'] = UserInformationForm()
        context['countries'] = Country.objects.all()
        context['today'] = timezone.now().date()
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        """Processa o formulário quando válido"""
        # 1. Salva o usuário
        user = form.save()
        
        # 2. Processa UserInformation
        user_info_form = UserInformationForm(self.request.POST)
        
        if user_info_form.is_valid():
            # Cria UserInformation sem salvar ainda
            user_info = user_info_form.save(commit=False)
            user_info.user = user
            
            # Define os campos de relacionamento
            country_id = self.request.POST.get('country')
            state_id = self.request.POST.get('state')
            city_id = self.request.POST.get('city')
            
            # Valida e obtém os objetos
            try:
                if country_id:
                    user_info.country = Country.objects.get(id=country_id)
                if state_id:
                    user_info.state = State.objects.get(id=state_id)
                if city_id:
                    user_info.city = City.objects.get(id=city_id)
                
                # Define os campos de auditoria
                user_info.created_by = user
                user_info.updated_by = user
                user_info.is_active = True
                
                # Salva o UserInformation
                user_info.save()
                
            except (Country.DoesNotExist, State.DoesNotExist, City.DoesNotExist):
                messages.error(self.request, "Localização inválida. Por favor, selecione novamente.")
                return self.form_invalid(form)
            
            # 3. Faz login automaticamente
            # CORREÇÃO: Especifica o backend para evitar o erro
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(self.request, user)
            
            messages.success(self.request, 'Cadastro realizado com sucesso!')
            return super().form_valid(form)
        else:
            # Se UserInformationForm não for válido
            return self.render_to_response(
                self.get_context_data(form=form, user_info_form=user_info_form)
            )
    
    def form_invalid(self, form):
        """Processa o formulário quando inválido"""
        user_info_form = UserInformationForm(self.request.POST)
        return self.render_to_response(
            self.get_context_data(form=form, user_info_form=user_info_form)
        )
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import City,State


@method_decorator(csrf_exempt, name='dispatch')
class GetStatesView(View):
    def get(self, request):
        country_id = request.GET.get('country_id')
        if country_id:
            states = State.objects.filter(country_id=country_id).order_by('name')
            data = [{'id': state.id, 'name': state.name} for state in states]
            return JsonResponse(data, safe=False)
        return JsonResponse([], safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class GetCitiesView(View):
    def get(self, request):
        state_id = request.GET.get('state_id')
        if state_id:
            cities = City.objects.filter(state_id=state_id).order_by('name')
            data = [{'id': city.id, 'name': city.name} for city in cities]
            return JsonResponse(data, safe=False)
        return JsonResponse([], safe=False)
    

class SiteCreateView(LoginRequiredMixin,CreateView):
    model = Site
    form_class = SiteForm
    template_name = 'core/site_form.html'
    success_url = reverse_lazy("select_site")

    def form_valid(self, form):
        # Salva o site primeiro
        site = form.save(commit=False)
        site.save()
        
        # Adiciona o criador como membro com papel de Site Owner
        owner_group = Group.objects.get(name='Site Manager')
        SiteMembership.objects.create(
            site=site,
            user=self.request.user,
            role=owner_group
        )
        
        messages.success(self.request, 'Site cadastrado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cadastro de Site'
        context['subtitle'] = 'Informe os dados do novo site'
        return context
    
@method_decorator(csrf_exempt, name='dispatch')
class UpdateMemberRoleView(LoginRequiredMixin, View):
    """
    View assíncrona para atualizar o papel (role) de um membro no site.
    """
    
    def post(self, request):
        site_id = request.session.get('selected_site_location')
        
        if not site_id:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum site selecionado'
            }, status=400)
        
        # Verificar se o usuário atual é gerente
        manager_group = Group.objects.get(name="Site Manager")
        is_manager = SiteMembership.objects.filter(
            user=request.user,
            site_id=site_id,
            role=manager_group
        ).exists()
        
        if not is_manager:
            return JsonResponse({
                'success': False,
                'error': 'Apenas gerentes podem alterar papéis'
            }, status=403)
        
        # Obter dados da requisição
        try:
            import json
            data = json.loads(request.body)
            member_id = data.get('member_id')
            new_role_name = data.get('new_role')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({
                'success': False,
                'error': 'Dados inválidos'
            }, status=400)
        
        if not member_id or not new_role_name:
            return JsonResponse({
                'success': False,
                'error': 'Dados incompletos'
            }, status=400)
        
        # Buscar a membership do usuário no site
        try:
            membership = SiteMembership.objects.get(
                id=member_id,
                site_id=site_id
            )
        except SiteMembership.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Membro não encontrado neste site'
            }, status=404)
        
        # VERIFICAÇÃO CRÍTICA: O usuário não pode alterar seu próprio papel
        if membership.user == request.user:
            return JsonResponse({
                'success': False,
                'error': 'Você não pode alterar seu próprio papel'
            }, status=400)
        
        # Buscar o novo grupo
        try:
            new_role = Group.objects.get(name=new_role_name)
        except Group.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Papel "{new_role_name}" não existe'
            }, status=400)
        
        # Verificar se não está tentando alterar o último gerente
        if membership.role.name == "Site Manager" and new_role_name != "Site Manager":
            # Contar quantos gerentes existem (excluindo o próprio usuário da contagem se for gerente)
            manager_count = SiteMembership.objects.filter(
                site_id=site_id,
                role__name="Site Manager"
            ).count()
            
            if manager_count <= 1:
                return JsonResponse({
                    'success': False,
                    'error': 'Não é possível remover o único gerente do site'
                }, status=400)
        
        # Atualizar o papel
        try:
            membership.role = new_role
            membership.clean()  # Validar
            membership.save()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': f'Papel atualizado para {new_role_name}',
            'new_role': new_role_name,
            'new_role_display': self.get_role_display_name(new_role_name),
            'updated_member_id': member_id
        })
    
    def get_role_display_name(self, role_name):
        """Converte o nome técnico do papel para display"""
        role_display_map = {
            'Site Manager': 'Gerente',
            'Technical Assistance': 'Técnico',
            'Employee': 'Colaborador'
        }
        return role_display_map.get(role_name, role_name)
    
@method_decorator(csrf_exempt, name='dispatch')
class RemoveMemberView(LoginRequiredMixin, View):
    """
    View assíncrona para remover um membro do site.
    """
    
    def post(self, request):
        site_id = request.session.get('selected_site_location')
        
        if not site_id:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum site selecionado'
            }, status=400)
        
        # Verificar se o usuário atual é gerente
        manager_group = Group.objects.get(name="Site Manager")
        is_manager = SiteMembership.objects.filter(
            user=request.user,
            site_id=site_id,
            role=manager_group
        ).exists()
        
        if not is_manager:
            return JsonResponse({
                'success': False,
                'error': 'Apenas gerentes podem remover membros'
            }, status=403)
        
        # Obter dados da requisição
        try:
            import json
            data = json.loads(request.body)
            member_id = data.get('member_id')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({
                'success': False,
                'error': 'Dados inválidos'
            }, status=400)
        
        if not member_id:
            return JsonResponse({
                'success': False,
                'error': 'ID do membro não fornecido'
            }, status=400)
        
        # Buscar a membership do usuário no site
        try:
            membership = SiteMembership.objects.get(
                id=member_id,
                site_id=site_id
            )
        except SiteMembership.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Membro não encontrado neste site'
            }, status=404)
        
        # VERIFICAÇÃO CRÍTICA: O usuário não pode remover a si mesmo
        if membership.user == request.user:
            return JsonResponse({
                'success': False,
                'error': 'Você não pode remover a si mesmo'
            }, status=400)
        
        # Verificar se não está tentando remover o último gerente
        if membership.role.name == "Site Manager":
            # Contar quantos gerentes existem
            manager_count = SiteMembership.objects.filter(
                site_id=site_id,
                role__name="Site Manager"
            ).count()
            
            if manager_count <= 1:
                return JsonResponse({
                    'success': False,
                    'error': 'Não é possível remover o único gerente do site'
                }, status=400)
        
        # Verificar se não está tentando remover um Site Owner
        if membership.role.name == "Site Owner":
            return JsonResponse({
                'success': False,
                'error': 'Não é possível remover o proprietário do site'
            }, status=400)
        
        # Remover o membro
        try:
            member_name = membership.user.get_full_name() or membership.user.email
            membership.delete()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': f'{member_name} removido do site',
            'removed_member_id': member_id
        })

from koltagri.landplots.models import Cultivation
from .forms import CultivationForm
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse
from django.shortcuts import redirect
from django.http import JsonResponse

# Adicionar estas views ao final do arquivo

class CultivationCreateView(LoginRequiredMixin, View):
    def post(self, request):
        site_id = request.session.get('selected_site_location')
        if not site_id:
            messages.error(request, 'Nenhum site selecionado.')
            return redirect('lands')
        
        form = CultivationForm(request.POST)
        if form.is_valid():
            cultivation = form.save(commit=False)
            cultivation.site_id = site_id
            cultivation.save()
            messages.success(request, 'Área criada com sucesso!')
        else:
            # Em caso de erro, adiciona as mensagens de erro
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return redirect('lands')


class CultivationUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        site_id = request.session.get('selected_site_location')
        
        try:
            cultivation = Cultivation.objects.get(pk=pk, site_id=site_id)
        except Cultivation.DoesNotExist:
            messages.error(request, 'Área não encontrada.')
            return redirect('lands')
        
        form = CultivationForm(request.POST, instance=cultivation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área atualizada com sucesso!')
        else:
            # Em caso de erro, adiciona as mensagens de erro
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return redirect('lands')


class CultivationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        site_id = request.session.get('selected_site_location')
        
        try:
            cultivation = Cultivation.objects.get(pk=pk, site_id=site_id)
            cultivation.delete()
            messages.success(request, 'Área excluída com sucesso!')
        except Cultivation.DoesNotExist:
            messages.error(request, 'Área não encontrada.')
        
        return redirect('lands')
    


    
class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "Você saiu com sucesso.")
        return redirect('login')  # Assumindo que você tem uma URL nomeada 'login'
    
    def get(self, request):
        # Também permite logout via GET para conveniência
        logout(request)
        messages.success(request, "Você saiu com sucesso.")
        return redirect('login')