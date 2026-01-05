from django.urls import path
from .views import IndexView, LoginView,RegisterView,NotificationsView,ProfileView,TeamView,LandsView,PropertyView,select_site_location,SelectSiteView
urlpatterns = [
    path("",IndexView.as_view(),name='index'),
    path("login/",LoginView.as_view(),name='login'),
    path("register/",RegisterView.as_view(),name='register'),
    path("notifications/",NotificationsView.as_view(), name="notifications"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("propriedade/participantes",TeamView.as_view(),name="team_participants"),
    path("propriedade/areas", LandsView.as_view(),name="lands"),
    path("propriedes/",PropertyView.as_view(),name= "property"),
    path("select-site/<int:site_id>/",select_site_location,name="select_site_location"),
    path("select-site/",SelectSiteView.as_view(),name="select_site"),
]
