from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError

from koltagri.core.mixins import SiteRequiredMixin
from koltagri.users.models import User
from .models import UserInformation
from koltagri.core.models import Country
from django.utils.dateparse import parse_date

class ProfileView( SiteRequiredMixin, TemplateView):
    template_name = 'profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Busca ou cria UserInformation para o usuário
        user_info, created = UserInformation.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'country': Country.objects.first(),  # País padrão
            }
        )
        
        context['user_info'] = user_info
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        
        try:
            user_info = UserInformation.objects.get(user=user)
        except UserInformation.DoesNotExist:
            # Se não existir, cria um novo
            user_info = UserInformation.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                country=Country.objects.first()
            )
        
        # Atualiza dados do User (apenas nome e email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Atualiza dados do UserInformation
        user_info.title = request.POST.get('title', user_info.title)
        user_info.first_name = request.POST.get('first_name', user_info.first_name)
        user_info.last_name = request.POST.get('last_name', user_info.last_name)
        user_info.cpf = request.POST.get('cpf', user_info.cpf)
        
        # Tratamento especial para o campo birth (data)
        birth_str = request.POST.get('birth', '')
        if birth_str:  # Se não estiver vazio
            try:
                # Tenta converter a string para data
                user_info.birth = parse_date(birth_str)
            except (ValueError, TypeError):
                # Se falhar, mantém o valor atual
                pass
        else:
            # Se estiver vazio, define como None
            user_info.birth = None
        
        user_info.zip_code = request.POST.get('zip_code', user_info.zip_code)
        user_info.phone = request.POST.get('phone', user_info.phone)
        
        # Atualiza foto de perfil se fornecida
        if 'profile_picture' in request.FILES:
            user_info.profile_picture = request.FILES['profile_picture']
        
        try:
            user_info.save()
            messages.success(request, "Perfil atualizado com sucesso!")
        except ValidationError as e:
            messages.error(request, f"Erro ao salvar: {', '.join(e.messages)}")
        
        return redirect('profile')

class SignupView(TemplateView):
    template_name = 'signup.html'

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