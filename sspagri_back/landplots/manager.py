
from django.db import models

class SiteMembershipActiveUsersManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                models.Q(user__users_information__isnull=True)
                | models.Q(user__users_information__is_active=True),
                user__is_active=True,
            )
        )


class CultivationManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                models.Q(user__users_information__isnull=True)
                | models.Q(user__users_information__is_active=True),
                user__is_active=True,
            )
        )