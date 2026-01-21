from django import forms
from .models import Expense, ExpensesCategory,AgriculturalInputs,AgriculturalInputPack,AgriculturalInputUsage
from django.utils import timezone
from django.core.exceptions import ValidationError

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'category', 'date', 'note']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do gasto'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ExpensesCategory.objects.all()

class AgriculturalInputValidationForm(forms.ModelForm):

    class Meta:
        model = AgriculturalInputs
        fields = ['name','description','unit','image']


class AgriculturalInputPackForm(forms.ModelForm):
    class Meta:
        model = AgriculturalInputPack
        fields = [
            "agricultural_input",
            "quantity",
            "purchase_date",
            "price",
        ]

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty is None:
            return qty
        if qty <= 0:
            raise ValidationError("Quantidade deve ser maior que zero.")
        return qty

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            return price
        if price < 0:
            raise ValidationError("Preço não pode ser negativo.")
        return price


class AgriculturalInputUsageForm(forms.ModelForm):
    class Meta:
        model = AgriculturalInputUsage
        fields = [
            "pack",
            "cultivation_plant",
            "quantity_used",
            "usage_date",
        ]
        widgets = {
            'pack': forms.HiddenInput(),  # Campo oculto, já que o pack é definido pela URL
        }

    def __init__(self, *args, **kwargs):
        # Extrai parâmetros específicos
        self.pack = kwargs.pop('pack', None)
        pack_queryset = kwargs.pop('pack_queryset', None)
        
        super().__init__(*args, **kwargs)
        
        # Se temos um pack específico
        if self.pack:
            # Configura o valor inicial
            self.fields['pack'].initial = self.pack
            
            # Limita o queryset apenas a este pack
            if pack_queryset is not None:
                self.fields['pack'].queryset = pack_queryset
            else:
                self.fields['pack'].queryset = AgriculturalInputPack.objects.filter(pk=self.pack.pk)
            
            # Configuração para evitar tentativa de selecionar outro pack
            self.fields['pack'].disabled = True
        else:
            # Se não houver pack, mostra apenas packs disponíveis
            packs = AgriculturalInputPack.objects.all()
            available_pks = [p.pk for p in packs if p.remaining_quantity() > 0]
            self.fields["pack"].queryset = AgriculturalInputPack.objects.filter(pk__in=available_pks)

    def clean_quantity_used(self):
        """Valida a quantidade usada"""
        qty = self.cleaned_data.get("quantity_used")
        if qty is None:
            return qty
        if qty <= 0:
            raise ValidationError("Quantidade usada deve ser maior que zero.")
        
        # Se temos um pack, valida contra o estoque
        if self.pack and qty:
            remaining = self.pack.remaining_quantity()
            if qty > remaining:
                raise ValidationError(
                    f"Quantidade indisponível. Restam apenas {remaining:.2f} "
                    f"{self.pack.agricultural_input.unit}"
                )
        
        return qty

    def clean(self):
        """Validação adicional"""
        cleaned = super().clean()
        
        # Se não tivermos pack no __init__, tenta pegar do formulário
        if not self.pack:
            pack = cleaned.get("pack")
            qty = cleaned.get("quantity_used")
            
            if pack and qty:
                remaining = pack.remaining_quantity()
                
                # Se for edição, ajusta para considerar o valor anterior
                if self.instance and self.instance.pk:
                    old_qty = self.instance.quantity_used
                    remaining = remaining + old_qty
                
                if qty > remaining:
                    raise ValidationError(
                        f"Quantidade indisponível. Restam apenas {remaining:.2f} "
                        f"{pack.agricultural_input.unit}"
                    )
        
        return cleaned