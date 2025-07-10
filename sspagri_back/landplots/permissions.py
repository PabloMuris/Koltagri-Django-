from rest_framework import permissions
from rest_framework.permissions import BasePermission
from sspagri_back.core.constants import (
    ROLE_SYSTEM_ADMIN,
    ROLE_SITE_OWNER,
    ROLE_SITE_MANAGER,
    ROLE_SITE_TEAM,
    ROLE_STUDY_TEAM,
    ROLE_STUDY_MANAGER)


class IsInGroupPermission(BasePermission):
    group_name = None

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            self.group_name and
            request.user.groups.filter(name=self.group_name).exists()
        )


class IsSystemAdmin(IsInGroupPermission):
    group_name = ROLE_SYSTEM_ADMIN


class IsSiteOwner(IsInGroupPermission):
    group_name = ROLE_SITE_OWNER


class IsSiteManager(IsInGroupPermission):
    group_name = ROLE_SITE_MANAGER


class IsSiteTeam(IsInGroupPermission):
    group_name = ROLE_SITE_TEAM


class IsStudyTeam(IsInGroupPermission):
    group_name = ROLE_STUDY_TEAM


class IsStudyManager(IsInGroupPermission):
    group_name = ROLE_STUDY_MANAGER