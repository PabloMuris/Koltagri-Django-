from django import forms
from .models import Expense, ExpensesCategory,AgriculturalInputs
from django.utils import timezone

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

class AgriculturalInputValidationForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(required=False)
    quantity = forms.DecimalField(max_digits=10, decimal_places=2)
    unit = forms.ChoiceField(choices=[
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Liter"),
        ("ml", "Milliliter"),
        ("pcs", "Pieces"),
    ])
    purchase_date = forms.DateField(required=False)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    image = forms.ImageField(required=False)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 3:
            raise forms.ValidationError("O nome precisa ter ao menos 3 caracteres.")
        return name

    def clean_purchase_date(self):
        return self.cleaned_data.get("purchase_date") or timezone.now().date()

    name = forms.CharField(max_length=200)
    description = forms.CharField(required=False)
    quantity = forms.DecimalField(max_digits=10, decimal_places=2)
    unit = forms.ChoiceField(choices=[
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Liter"),
        ("ml", "Milliliter"),
        ("pcs", "Pieces"),
    ])
    purchase_date = forms.DateField(required=False)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    image = forms.ImageField(required=False)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 3:
            raise forms.ValidationError("O nome precisa ter ao menos 3 caracteres.")
        return name

    def clean_purchase_date(self):
        return self.cleaned_data.get("purchase_date") or timezone.now().date()

    class Meta:
        model = AgriculturalInputs
        fields = ['name','description', 'quantity', 'unit', 'purchase_date','price', ]

        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'supply-name', 
                'placeholder': 'Nome do insumo',
            }),
            'quantity': forms.NumberInput(attrs={
                'id': 'supply-quantity', 
                'placeholder': 'Quantidade',
                'step': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'id': 'supply-unit-price', 
                'placeholder': 'Preço unitário',
                'step': '0.01'
            }),
            'supplier': forms.TextInput(attrs={
                'id': 'supply-supplier', 
                'placeholder': 'Fornecedor',
            }),
            'purchase_date': forms.DateInput(attrs={
                'id': 'supply-purchase-date', 
                'type': 'date' 
            }),
        }