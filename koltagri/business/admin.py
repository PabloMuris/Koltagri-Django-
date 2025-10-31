from django.contrib import admin
# Importe seus modelos (ajuste '.models' se estiver em um local diferente)
from .models import ExpensesCategory, Expense, IncomeCategory, Income

@admin.register(ExpensesCategory)
class ExpensesCategoryAdmin(admin.ModelAdmin):
    """
    Admin para Categoria de Despesa.
    """
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Admin para Despesas com filtros e ordenação.
    """
    list_display = ('date', 'category', 'amount', 'description')
    
    # Requisito: Filtrar por categoria e por data
    list_filter = ('category', 'date')
    
    # Requisito: Mostrar o 'mais recente' primeiro
    ordering = ('-date',)
    
    # Bônus: Campo de busca
    search_fields = ('description', 'category__name')

@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    """
    Admin para Categoria de Receita.
    """
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    """
    Admin para Receitas com filtros e ordenação.
    """
    list_display = ('date', 'category', 'amount', 'description')
    
    # Requisito: Filtrar por categoria e por data
    list_filter = ('category', 'date')
    
    # Requisito: Mostrar o 'mais recente' primeiro
    ordering = ('-date',)
    
    # Bônus: Campo de busca
    search_fields = ('description', 'category__name')