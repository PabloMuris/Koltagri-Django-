from django.urls import path,re_path
from .views import BusinessDashboardView,PlanningView,StatisticsView
urlpatterns = [
   path("",BusinessDashboardView.as_view(),name="business_board"),
   path("planning/",PlanningView.as_view(),name="planning"),
   path("statistics/",StatisticsView.as_view(),name="statistics"),
]
