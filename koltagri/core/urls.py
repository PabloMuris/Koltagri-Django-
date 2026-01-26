from django.urls import path
from .views import (IndexView,
                     LoginView,
                     RegisterView
                     ,NotificationsView,
                     ProfileView,TeamView,
                     LandsView,
                     PropertyView,
                     select_site_location,
                     SelectSiteView,
                     AcceptInviteView,
                     CreateInviteView,
                     GetCitiesView, 
                     GetStatesView,
                     SiteCreateView,
                     UpdateMemberRoleView,
                     RemoveMemberView,
                     CultivationCreateView,
                     CultivationUpdateView,
                     CultivationDeleteView,
                     LogoutView
                     
)

urlpatterns = [
    path("",IndexView.as_view(),name='index'),
    path("login/",LoginView.as_view(),name='login'),
    path("register/",RegisterView.as_view(),name='register'),
    path("notifications/",NotificationsView.as_view(), name="notifications"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("propriedade/participantes",TeamView.as_view(),name="team_participants"),
    path("propriedade/areas", LandsView.as_view(),name="lands"),
    path("propriedes/",PropertyView.as_view(),name= "property"),
    path("locais/<int:site_id>/",select_site_location,name="select_site_location"),
    path("locais/",SelectSiteView.as_view(),name="select_site"),
        path("locais/nova_propriedade", SiteCreateView.as_view(), name="create_site"),

    path(
        "sites/<int:site_id>/invite/",
        CreateInviteView.as_view(),
        name="create-invite"
    ),
    path(
        "invites/accept/<uuid:token>/",
        AcceptInviteView.as_view(),
        name="accept-invite"
    ),
    path('api/cities/', GetCitiesView.as_view(), name='get_cities'),
    path('api/states/', GetStatesView.as_view(), name='get_states'),
    path(
        "team/update-role/",
        UpdateMemberRoleView.as_view(),
        name="update_member_role"
    ),
    path(
        "team/remove-member/",
        RemoveMemberView.as_view(),
        name="remove_member"
    ),
    path("areas/nova/", CultivationCreateView.as_view(), name="cultivation_create"),
path("areas/<int:pk>/editar/", CultivationUpdateView.as_view(), name="cultivation_update"),
path("areas/<int:pk>/excluir/", CultivationDeleteView.as_view(), name="cultivation_delete"),
path('logout/', LogoutView.as_view(), name='logout')
]
