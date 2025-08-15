from django.conf import settings
from django.db import models


class PasswordHistoryQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)

    def by_recents_rule(self, user):
        return self.by_user(user).order_by("-created_at")[
            : settings.PASSWORD_REPETITION_TIME_LIMIT
        ]


class UserInformationQuerySet(models.QuerySet):
    def by_full_name(self, fullname):
        return self.annotate(
            fullname=models.functions.Concat(
                models.F("first_name"),
                models.Value(" "),
                models.F("last_name"),
                output_field=models.CharField(),
            )
        ).filter(fullname__icontains=fullname)


