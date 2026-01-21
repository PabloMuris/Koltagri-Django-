# koltagri/core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

from koltagri.users.models import User
from koltagri.person.models import UserInformation
from koltagri.core.models import Country, City,State

from koltagri.landplots.models import Site
import zoneinfo

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email já está cadastrado.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # O username será o email
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserInformationForm(forms.ModelForm):
    cpf = forms.CharField(
        required=True,
        max_length=14,
        help_text="Digite apenas números"
    )
    
    # Adicione o campo state
    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        required=True,
        label="Estado"
    )
    
    class Meta:
        model = UserInformation
        fields = ('cpf', 'birth', 'phone', 'country', 'state', 'city')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Estado: filtra por país
        self.fields['state'].queryset = State.objects.none()
        self.fields['city'].queryset = City.objects.none()
        
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.country:
            self.fields['state'].queryset = self.instance.country.states.order_by('name')
        
        # Cidade: filtra por estado
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.state:
            self.fields['city'].queryset = self.instance.state.cities.order_by('name')
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        if len(cpf_numeros) != 11:
            raise ValidationError("CPF deve ter 11 dígitos.")
        
        # Verifica se CPF já existe
        if UserInformation.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError("Este CPF já está cadastrado.")
        
        return cpf_numeros
    

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["name", "country", "timezone"]
        widgets = {
            'timezone': forms.Select(choices=[(tz, tz) for tz in zoneinfo.available_timezones()]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Opcional: melhorar a apresentação dos campos
        self.fields["name"].widget.attrs.update({
            "placeholder": "Ex: Fazenda Santa Maria"
        })
        
        # Ordenar países por nome
        self.fields["country"].queryset = Country.objects.all().order_by('name')
        
        # Adicionar classes CSS para consistência
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
    
    def clean_timezone(self):
        timezone = self.cleaned_data.get('timezone')
        if timezone not in zoneinfo.available_timezones():
            raise forms.ValidationError("Fuso horário inválido")
        return timezone