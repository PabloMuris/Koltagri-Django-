import django_filters
from .models import Expense,ExpensesCategory
from django import forms

class ExpenseFilter(django_filters.FilterSet):
    # Filtro por data específica
    date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="exact",
        label="Data específica",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # Filtro por intervalo de datas
    date_range = django_filters.DateFromToRangeFilter(
        field_name="date",
        label="Intervalo de datas",
        widget=django_filters.widgets.RangeWidget(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'DD/MM/YYYY'
            }
        )
    )
    
    # Filtro por categoria
    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=ExpensesCategory.objects.all(),
        label="Categoria",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Filtro por descrição
    description = django_filters.CharFilter(
        field_name="description",
        lookup_expr="icontains",
        label="Descrição",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar na descrição...'
        })
    )
    
    # Filtro por valor mínimo
    amount_min = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="gte",
        label="Valor mínimo",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    # Filtro por valor máximo
    amount_max = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="lte",
        label="Valor máximo",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )

    class Meta:
        model = Expense
        fields = ['category', 'date', 'description', 'amount']