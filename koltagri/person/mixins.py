import uuid



from django.utils.translation import gettext_lazy as _




import koltagri.core.constants as core_constants





class ModelRolesMixin:

    @property
    def is_site_owner(self):
        return self.group.name == core_constants.ROLE_SITE_OWNER
    
    @property
    def is_site_manager(self):
        return self.group.name == core_constants.ROLE_SITE_MANAGER

    @property
    def is_site_team(self):
        return self.group.name == core_constants.ROLE_SITE_TEAM

    @property
    def is_site_member(self):
        return (
            self.group.name == core_constants.ROLE_SITE_TEAM
            or self.group.name == core_constants.ROLE_SITE_MANAGER
            or self.group.name == core_constants.ROLE_SITE_OWNER
        )
    

   

import uuid



from django.utils.translation import gettext_lazy as _


from koltagri.core.constants import (
    ROLE_SITE_OWNER,
    ROLE_SITE_MANAGER,
    ROLE_TECNICAL_ASSISTANCE,
    ROLE_EMPLOYEE,
)

from django.contrib.auth.mixins import AccessMixin

class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.groups.filter(
            name__in=self.allowed_roles
        ).exists():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

class SiteOwnerRequiredMixin(RoleRequiredMixin):
    allowed_roles = [core_constants.ROLE_SITE_OWNER]


class SiteManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = [core_constants.ROLE_SITE_MANAGER]


class TechnicalAssistanceRequiredMixin(RoleRequiredMixin):
    allowed_roles = [core_constants.ROLE_TECNICAL_ASSISTANCE]


class EmployeeRequiredMixin(RoleRequiredMixin):
    allowed_roles = [core_constants.ROLE_EMPLOYEE]

class TechnicalOrAboveRequiredMixin(RoleRequiredMixin):
    allowed_roles = [
        ROLE_SITE_OWNER,
        ROLE_SITE_MANAGER,
        ROLE_TECNICAL_ASSISTANCE,
    ]

class ManagerOrAboveRequiredMixin(RoleRequiredMixin):
    allowed_roles = [
        ROLE_SITE_OWNER,
        ROLE_SITE_MANAGER,
    ]