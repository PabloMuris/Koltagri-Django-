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

    def __init__(self, *args, only_available_packs=True, **kwargs):
        super().__init__(*args, **kwargs)
        # opcional: mostrar só packs que ainda têm saldo
        if only_available_packs:
            packs = AgriculturalInputPack.objects.all()
            available_pks = [p.pk for p in packs if p.remaining_quantity() > 0]
            self.fields["pack"].queryset = AgriculturalInputPack.objects.filter(pk__in=available_pks)

    def clean_quantity_used(self):
        qty = self.cleaned_data.get("quantity_used")
        if qty is None:
            return qty
        if qty <= 0:
            raise ValidationError("Quantidade usada deve ser maior que zero.")
        return qty

    def clean(self):
        cleaned = super().clean()
        pack = cleaned.get("pack")
        qty = cleaned.get("quantity_used")
        if pack and qty is not None:
            remaining = pack.remaining_quantity()
            # Se for edição de um usage existente, é preciso permitir re-subtrair o próprio valor,
            # mas como esse é o form de criação simples, bloqueamos excesso aqui.
            if qty > remaining:
                raise ValidationError(f"Quantidade indisponível no pack. Restam apenas {remaining}.")
        return cleaned