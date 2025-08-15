from django.db import models

# Create your models here.

import uuid


from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models, transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _


from koltagri.core.models import BaseModel, BaseModelWithSoftDelete, SoftDeleteModel,Country

from .managers import UserInformationManager,UserProfileManager,PasswordHistoryManager,ActivesUserInformationManager

from .querysets import PasswordHistoryQuerySet

import koltagri.core.constants as core_constants

from .querysets import UserInformationQuerySet

class ModelRolesMixin:
    
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

    #@property
    #def is_admin(self):
        #return any(
            #[self.is_thalocan_admin, self.is_sponsor_manager, self.is_study_team]
        #)

    #@property
    #def is_user_manager(self):
        #return self.group.name in core_constants.MANAGEMENT_GROUP_HIERARCHY.keys()






class UserProfile(SoftDeleteModel, ModelRolesMixin):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_profile"
    )

    site = models.ForeignKey("landplots.Site", on_delete=models.PROTECT, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    objects = UserProfileManager()

    @classmethod
    def create_invited_site_user_profile(cls, user, role, site, study):
        group = Group.objects.get(name=role)
        profile = cls.objects.create(user=user, group=group, site=site, study=study)
        return profile

    @transaction.atomic
    def deactivate(self):
        user_information = getattr(self.user, "users_information", None)
        if user_information and user_information.last_user_profile == self:
            user_information.last_user_profile = self.user.user_profile.exclude(
                pk=self.pk
            ).first()
            user_information.save(update_fields=["last_user_profile"])
        self.is_active = False
        self.save(update_fields=["is_active"])





class UserInformation(BaseModelWithSoftDelete):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        related_name="users_information",
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        verbose_name="Title",
        blank=True,
    )
    first_name = models.CharField(
        verbose_name=_("First name"),
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),

    )
    
    birth = models.DateField("Birth", blank=True, null=True)
    zip_code = models.CharField(
        verbose_name="Zip Code",
        blank=True,
    )
    phone = models.CharField(
        verbose_name="Phone Number",
        blank=True,
    )
    last_user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="last_profile_of_user",
    )
    city = models.CharField(
        _("City"),
        blank=True,
        null=True,
    )

    country = models.ForeignKey(Country, verbose_name=_(""), on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pictures",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(_("Is active"), default=True)

    objects = UserInformationManager.from_queryset(UserInformationQuerySet)()
    actives = ActivesUserInformationManager.from_queryset(
        UserInformationQuerySet
    )()

    class Meta:
        verbose_name = _("User information")
        verbose_name_plural = _("Users information")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.is_deleted and not self._state.adding:
            unique_suffix = uuid.uuid5().hex
            self.email = f"{self.email}__deleted__{unique_suffix}"
        super().save(*args, **kwargs)

    @property
    def formal_name(self):
        return f"{self.title} {self.full_name}".strip()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @method_decorator(transaction.atomic)
    def deactivate(self, requester):
        self.is_active = False
        self.last_user_profile = None
        self.updated_by = requester
        self.save(update_fields=["is_active", "last_user_profile", "updated_by"])
        self.user.user_profile.deactivate()
        self.user.sitemembership_set.all().delete()
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

    @method_decorator(transaction.atomic)
    def reactivate(self, requester):
        self.is_active = True
        self.updated_by = requester
        self.save(update_fields=["is_active", "updated_by"])
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])

