from django import forms
from .models import Expense, ExpensesCategory,AgriculturalInputs

class ExpenseForm(forms.ModelForm):
 
    category = forms.ModelChoiceField(
        queryset=ExpensesCategory.objects.all(), 
        empty_label="Selecione uma categoria",
     
        widget=forms.Select(attrs={'id': 'add-category'})
    )

    class Meta:
        model = Expense
        fields = ['description', 'amount', 'category', 'date', 'note']
        
        
        widgets = {
            'description': forms.TextInput(attrs={
                'id': 'add-description', 
                'placeholder': 'Ex: Compra de fertilizantes',
               
            }),
            'amount': forms.NumberInput(attrs={
                'id': 'add-amount', 
                'placeholder': '0,00',
                'step': '0.01'
            }),
            'date': forms.DateInput(attrs={
                'id': 'add-date', 
                'type': 'date' 
            }),
            'note': forms.Textarea(attrs={
                'id': 'add-notes', 
                'placeholder': 'Detalhes adicionais sobre este gasto...',
                'rows': 3  
            }),
        }

class SuppliesForm(forms.ModelForm):
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