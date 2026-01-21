from django.contrib import admin
# Importe seus modelos (ajuste '.models' se estiver em um local diferente)
from .models import (
    ExpensesCategory, 
    Expense, 
    IncomeCategory, 
    Income,
    AgriculturalInputs,
    AgriculturalInputPack,
    AgriculturalInputUsage)

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




# =========================
# USAGES (INLINE DO PACK)
# =========================
class AgriculturalInputUsageInline(admin.TabularInline):
    model = AgriculturalInputUsage
    extra = 0
    fields = (
        "cultivation_plant",
        "quantity_used",
        "usage_date",
    )
    autocomplete_fields = ("cultivation_plant",)


# =========================
# PACKS (INLINE DO INPUT)
# =========================
class AgriculturalInputPackInline(admin.TabularInline):
    model = AgriculturalInputPack
    extra = 0
    fields = (
        "name",
        "quantity",
        "price",
        "purchase_date",
        "remaining_quantity_display",
        "is_depleted_display",
    )
    readonly_fields = (
        "name",
        "remaining_quantity_display",
        "is_depleted_display",
    )
    show_change_link = True

    def remaining_quantity_display(self, obj):
        return obj.remaining_quantity()
    remaining_quantity_display.short_description = "Quantidade restante"

    def is_depleted_display(self, obj):
        return "Sim" if obj.is_depleted() else "Não"
    is_depleted_display.short_description = "Esgotado"


# =========================
# AGRICULTURAL INPUTS
# =========================
@admin.register(AgriculturalInputs)
class AgriculturalInputsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "unit",
    )
    list_filter = ("unit",)
    search_fields = ("name",)
    inlines = (AgriculturalInputPackInline,)
    ordering = ("name",)


# =========================
# PACKS (ADMIN DIRETO)
# =========================
@admin.register(AgriculturalInputPack)
class AgriculturalInputPackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "agricultural_input",
        "quantity",
        "price",
        "purchase_date",
        "remaining_quantity_display",
        "is_depleted_display",
    )
    list_filter = (
        "purchase_date",
        "agricultural_input__unit",
    )
    search_fields = (
        "name",
        "agricultural_input__name",
    )
    readonly_fields = ("name",)
    inlines = (AgriculturalInputUsageInline,)

    def remaining_quantity_display(self, obj):
        return obj.remaining_quantity()
    remaining_quantity_display.short_description = "Restante"

    def is_depleted_display(self, obj):
        return "Sim" if obj.is_depleted() else "Não"
    is_depleted_display.short_description = "Esgotado"


# =========================
# USAGES (ADMIN DIRETO)
# =========================
@admin.register(AgriculturalInputUsage)
class AgriculturalInputUsageAdmin(admin.ModelAdmin):
    list_display = (
        "pack",
        "cultivation_plant",
        "quantity_used",
        "usage_date",
    )
    list_filter = ("usage_date",)
    search_fields = (
        "pack__name",
        "cultivation_plant__name",
    )
    autocomplete_fields = ("pack", "cultivation_plant")
