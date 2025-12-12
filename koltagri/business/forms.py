from django import forms
from .models import Expense, ExpensesCategory

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