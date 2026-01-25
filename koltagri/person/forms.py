# koltagri/person/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import UserInformation

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu.email@exemplo.com'
        })
    )
    
    first_name = forms.CharField(
        required=True,
        label=_("Primeiro Nome"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu primeiro nome'
        })
    )
    
    last_name = forms.CharField(
        required=True,
        label=_("Sobrenome"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    
    birth = forms.DateField(
        required=False,
        label=_("Data de Nascimento"),
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = UserInformation
        fields = [
            'title', 'first_name', 'last_name', 'cpf',
            'birth', 'zip_code', 'phone', 'profile_picture'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sr., Sra., Dr.'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['email'].initial = self.user.email
            
        # Permite campo birth vazio
        self.fields['birth'].required = False
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        if cpf:
            # Remove caracteres não numéricos para validação
            cpf_clean = ''.join(filter(str.isdigit, cpf))
            if len(cpf_clean) != 11:
                raise ValidationError("CPF deve conter 11 dígitos.")
        return cpf
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            # Remove caracteres não numéricos para validação
            phone_clean = ''.join(filter(str.isdigit, phone))
            if len(phone_clean) not in [10, 11]:
                raise ValidationError("Telefone deve conter 10 ou 11 dígitos.")
        return phone
    
    def save(self, commit=True):
        user_info = super().save(commit=False)
        
        # Atualiza também o usuário principal
        if self.user:
            self.user.email = self.cleaned_data.get('email')
            self.user.first_name = self.cleaned_data.get('first_name')
            self.user.last_name = self.cleaned_data.get('last_name')
            self.user.save()
        
        if commit:
            user_info.save()
        
        return user_info