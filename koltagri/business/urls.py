from django.urls import path,re_path
from .views import (
   BusinessDashboardView,
   StatisticsView,
   SuppliesView,
   SuppliesDetailView,
   SuppliesListView,
   ExpenseCreateUpdateView,
   AgriculturalInputCreateUpdateView,
   SupplieDeleteView,
   ExpenseUpdateView,
   ExpenseDeleteView,
   expense_data_view,
   AgriculturalInputPackCreateView,
   AgriculturalInputPackDetailView,
   AgriculturalInputPackUpdateView,
   AgriculturalInputPackListView,
   AgriculturalInputUsageCreateView,
   AgriculturalInputPackDeleteView,
   PackUsagesListView,
   GenerateExpenseReportView
)
urlpatterns = [
   path("",BusinessDashboardView.as_view(),name="business_board"),
   path("gastos/",StatisticsView.as_view(),name="statistics"),
   path("insumos/",SuppliesListView.as_view(),name="supplies"),
   path("insumos/insumo/<int:pk>/",SuppliesDetailView.as_view(),name="supplies_detail"),
   path("insumos/novo-insumo/",AgriculturalInputCreateUpdateView.as_view(),name="supplies_form"), 
   path("insumos/editar-insumo/<int:pk>/",AgriculturalInputCreateUpdateView.as_view(),name="supplies_form_edit"),
   path("gastos",ExpenseCreateUpdateView.as_view(),name="expense_create_update"),
   path("insumo/deletar/<int:pk>/",SupplieDeleteView.as_view(),name="supplies_delete"),
   path("gastos/editar/<int:pk>/",ExpenseUpdateView.as_view(),name="expense_edit"),
   path("gastos/deletar/<int:pk>",ExpenseDeleteView.as_view(),name='expense_delete'),
   path("api/expense-data/", expense_data_view, name="expense_data"),
   path("insumos/insumo/<int:supplie_pk>/pacotes/", AgriculturalInputPackListView.as_view(), name="packs_list"),
   path("insumos/insumo/<int:supplie_pk>/pacotes/add/", AgriculturalInputPackCreateView.as_view(), name="pack_add"),
   path("insumos/insumo/<int:supplie_pk>/pacotes/<int:pk>/edit/", AgriculturalInputPackUpdateView.as_view(), name="pack_edit"),
   path("pacotes/<int:pk>/", AgriculturalInputPackDetailView.as_view(), name="pack_detail"),
   path("insumos/insumo/<int:supplie_pk>/pacotes/<int:pk>/usar",AgriculturalInputUsageCreateView.as_view(),name='pack_usage'),
   path(
        "insumos/insumo/<int:supplie_pk>/pacotes/<int:pk>/excluir/", 
        AgriculturalInputPackDeleteView.as_view(), 
        name="pack_delete"
    ),
       path("insumos/insumo/<int:supplie_pk>/pacotes/<int:pk>/usos",PackUsagesListView.as_view(),name='pack_uses'),
       path("relatorio-gastos/", GenerateExpenseReportView.as_view(), name="generate_expense_report"),

   
]
