from rest_framework import permissions
from rest_framework.permissions import BasePermission
from koltagri.core.constants import (
    ROLE_EMPLOYEE,
    ROLE_TECNICAL_ASSISTANCE,
    ROLE_SITE_MANAGER
)

from .models import SiteMembership

class IsInGroupPermissionMixin(BasePermission):
    required_roles = None  # agora no plural

    def has_permission(self, request, view):
        site_id = (
            view.kwargs.get('site_id') or
            request.data.get('site') or
            request.query_params.get('site')
        )

        if not request.user or not request.user.is_authenticated:
            return False

        if not self.required_roles or not site_id:
            return False

        # garante que sempre será uma lista
        roles = self.required_roles
        if not isinstance(roles, (list, tuple, set)):
            roles = [roles]

        return SiteMembership.objects.filter(
            user=request.user,
            site_id=site_id,
            role__name__in=roles
        ).exists()


class IsEmployeePermission(IsInGroupPermissionMixin):
    required_roles = ROLE_EMPLOYEE


class IsTechnicalAssistancePermission(IsInGroupPermissionMixin):
    required_roles = [
        ROLE_EMPLOYEE,
        ROLE_SITE_MANAGER
    ]

class IsStaffPermission(IsInGroupPermissionMixin):
    required_roles = (
        ROLE_EMPLOYEE,
        ROLE_SITE_MANAGER,
        ROLE_TECNICAL_ASSISTANCE
    )
