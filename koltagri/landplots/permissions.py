from rest_framework import permissions
from rest_framework.permissions import BasePermission
from koltagri.core.constants import (
    ROLE_SYSTEM_ADMIN,
    ROLE_SITE_OWNER,
    ROLE_SITE_MANAGER,
    ROLE_SITE_TEAM,
    ROLE_STUDY_TEAM,
    ROLE_STUDY_MANAGER)

from .models import SiteMembership

class IsInGroupPermission(BasePermission):
    required_role = None 

    def has_permission(self, request, view):
        site_id = (
            view.kwargs.get('site_id') or
            request.data.get('site') or
            request.query_params.get('site')
        )

        if not request.user or not request.user.is_authenticated:
            return False

        if not self.required_role or not site_id:
            return False

        return SiteMembership.objects.filter(
            user=request.user,
            site_id=site_id,
            role__name=self.required_role
        ).exists()




class IsSiteOwner(IsInGroupPermission):
    required_role = ROLE_SITE_OWNER


class IsSiteManager(IsInGroupPermission):
    required_role = ROLE_SITE_MANAGER


class IsSiteTeam(IsInGroupPermission):
    required_role = ROLE_SITE_TEAM

