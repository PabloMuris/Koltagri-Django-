from django.urls import path,re_path
from .views import BusinessDashboardView,StatisticsView,SuppliesView,SuppliesDetailView,SuppliesFormView,ExpenseCreateUpdateView
urlpatterns = [
   path("",BusinessDashboardView.as_view(),name="business_board"),
   path("gastos/",StatisticsView.as_view(),name="statistics"),
   path("insumos/",SuppliesFormView.as_view(),name="supplies"),
   path("insumos/insumo",SuppliesDetailView.as_view(),name="supplies_detail"),
   path("insumos/novo-insumo",SuppliesFormView.as_view(),name="supplies_form"), 
   path("gastos",ExpenseCreateUpdateView.as_view(),name="expense_create_update"),
]
