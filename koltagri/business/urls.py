from django.urls import path,re_path
from .views import (
   BusinessDashboardView,
   StatisticsView,
   SuppliesView,
   SuppliesDetailView,
   SuppliesFormView,
   ExpenseCreateUpdateView,
   AgriculturalInputCreateUpdateView,
   SupplieDeleteView,
   ExpenseUpdateView,
   ExpenseDeleteView,
   expense_data_view
)
urlpatterns = [
   path("",BusinessDashboardView.as_view(),name="business_board"),
   path("gastos/",StatisticsView.as_view(),name="statistics"),
   path("insumos/",SuppliesFormView.as_view(),name="supplies"),
   path("insumos/insumo/<int:pk>/",SuppliesDetailView.as_view(),name="supplies_detail"),
   path("insumos/novo-insumo/",AgriculturalInputCreateUpdateView.as_view(),name="supplies_form"), 
   path("insumos/editar-insumo/<int:pk>/",AgriculturalInputCreateUpdateView.as_view(),name="supplies_form_edit"),
   path("gastos",ExpenseCreateUpdateView.as_view(),name="expense_create_update"),
   path("insumo/deletar/<int:pk>/",SupplieDeleteView.as_view(),name="supplies_delete"),
   path("gastos/editar/<int:pk>/",ExpenseUpdateView.as_view(),name="expense_edit"),
   path("gastos/deletar/<int:pk>",ExpenseDeleteView.as_view(),name='expense_delete'),
   path("expense-data/", expense_data_view, name="expense_data"),
]
