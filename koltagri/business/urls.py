from django.urls import path,re_path
from .views import BusinessDashboardView,PlanningView
urlpatterns = [
   path("",BusinessDashboardView.as_view(),name="business_dashboard"),
   path("planning/",PlanningView.as_view(),name="planning"),
]
