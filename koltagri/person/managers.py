from django.db import models

from koltagri.core.manager import SoftDeleteManager


class UserInformationManager(SoftDeleteManager):
    def update_last_user_profile(self, user, user_profile):
        user_information, created = self.get_or_create(user=user)
        user_information.last_user_profile = user_profile
        user_information.save()
        return user_information

    """ return the last user profile of the user """

    def get_last_user_profile(self, user):
        user_information = self.get(user=user)

        # if the last user profile is not set, set it
        if not user_information.last_user_profile:
            from koltagri.person.models import UserProfile

            user_profile = UserProfile.objects.filter(
                user=user, is_active=True, is_deleted=False
            ).first()
            user_information.last_user_profile = user_profile
            user_information.save()
        return user_information


class ActivesUserInformationManager(SoftDeleteManager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class UserProfileManager(SoftDeleteManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)

    def by_study_and_site(self, study, site, user):
        return self.get_queryset().filter(study=study, site=site, user=user)

    def get_by_study_and_site(self, user, study, site):
        return self.by_study_and_site(study=study, site=site, user=user).first()

    def get_current_by_user(self, user):
        lookups = {"user": user}
        if (
            not self.get_queryset()
            .filter(group__name__in=self.model.ROLES_WITH_UNIQUE_PROFILE, **lookups)
            .exists()
        ):
            lookups["last_profile_of_user__isnull"] = False
        return self.get_queryset().get(**lookups)

    def deactivate(self):
        return self.get_queryset().update(is_active=False)


class PasswordHistoryManager(models.Manager):
    def get_last_record(self, user):
        return self.by_user(user).latest("created_at")

    def get_last_used_passwords(self, user):
        return self.by_recents_rule(user).values_list("password", flat=True)
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

    def by_site_candidates(self, site):
        return (
            self.exclude(user__sitemembership__site=site)
            .filter(
                models.Q(user__sitemembership__isnull=False)
                | models.Q(user__user_profile__group__name__in=ROLES_SITE_MEMBERS)
            )
            .distinct()
        )

    def by_site_number(self, site_number):
        return self.filter(user__user_profile__site__number=site_number)

    def by_study_site_candidates(self, site, study):
        from thalocan.person.models import UserProfile

        high_profiles = UserProfile.all_objects.filter(
            group__name__in=MANAGEMENT_GROUP_HIERARCHY[ROLES_THALOCAN_ADMIN]
        )
        return self.exclude(
            models.Q(
                user__user_profile__in=high_profiles,
            )
            | models.Q(
                user__user_profile__study_id=study,
                user__user_profile__site_id=site,
                user__user_profile__is_active=True,
                user__user_profile__is_deleted=False,
            )
        )

    def by_study(self, study):
        return self.filter(user__user_profile__study=study)

    def by_role(self, role, study=None, site=None):
        if role == ROLES_SITE_MEMBER:
            role_filter = models.Q(
                user__user_profile__group__name__in=ROLES_SITE_MEMBERS
            )
        else:
            role_filter = models.Q(user__user_profile__group__name=role)

        user_profile_filters = [role_filter]
        if study is not None:
            user_profile_filters.append(
                models.Q(user__user_profile__study__isnull=True)
                | models.Q(user__user_profile__study=study)
            )
        if site is not None:
            user_profile_filters.append(
                models.Q(user__user_profile__site__isnull=True)
                | models.Q(user__user_profile__site=site)
            )

        active_profiles = self.filter(
            *user_profile_filters,
            user__user_profile__is_active=True,
            user__user_profile__is_deleted=False,
        ).values("id")

        if site is not None:
            site_memberships = self.exclude(pk__in=active_profiles).filter(
                role_filter, user__sitemembership__site=site
            )
        else:
            site_memberships = self.none()

        site_memberships = site_memberships.values("id")

        inactive_profiles = self.exclude(pk__in=active_profiles)
        if site_memberships.exists():
            inactive_profiles = inactive_profiles.exclude(pk__in=site_memberships)

        inactive_profiles = inactive_profiles.filter(
            *user_profile_filters, user__user_profile__is_active=False, is_active=False
        ).values("id")

        return self.filter(
            pk__in=active_profiles.union(site_memberships, inactive_profiles)
        )
