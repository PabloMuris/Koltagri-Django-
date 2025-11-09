from django.urls import path,re_path
from .views import BusinessDashboardView,StatisticsView,SuppliesView,SuppliesDetailView
urlpatterns = [
   path("",BusinessDashboardView.as_view(),name="business_board"),
   path("gastos/",StatisticsView.as_view(),name="statistics"),
   path("insumos/",SuppliesView.as_view(),name="supplies"),
   path("insumo",SuppliesDetailView.as_view(),name="supplies_detail")
]
