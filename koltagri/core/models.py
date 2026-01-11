from django.db import models

# Create your models here.

import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from .manager import SoftDeleteManager
# Create your models here.
User = get_user_model()

from django.conf import settings
from django.utils import timezone


def get_sentinel_user():
    return get_user_model().objects.get_or_create(email="deleted")[0]


class UUIDModel(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4,null=True)

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    objects = SoftDeleteManager()
    all_objects = (
        models.Manager()
    )  

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


class CreationTimestampedModel(models.Model):
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
        editable=False,
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        on_delete=models.SET(get_sentinel_user),
        null=True,
        related_name="created_%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True


class UpdateTimestampedModel(models.Model):
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(
        User,
        verbose_name=_("Updated by"),
        on_delete=models.SET(get_sentinel_user),
        null=True,
        related_name="updated_%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True


class TimestampedModel(CreationTimestampedModel, UpdateTimestampedModel):
    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    class Meta:
        abstract = True


class BaseModelWithSoftDelete(BaseModel, SoftDeleteModel):
    class Meta:      
        abstract = True


class Country(models.Model):
    name = models.CharField(
        verbose_name=_("Name"), unique=True
    )
    abbreviation = models.CharField(
        verbose_name=_("Abbreviation"), max_length=3, unique=True
    )

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ["name"]

    def __str__(self):
        return self.abbreviation
    
class State(models.Model):
    name = models.CharField(
        verbose_name=_("Name"), max_length=100
    )
    

    country = models.ForeignKey(
        Country,
        verbose_name=_("Country"),
        on_delete=models.CASCADE,
        related_name="states"
    )

    class Meta:
        verbose_name = _("State")
        verbose_name_plural = _("States")
        ordering = ["name"]

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(
        verbose_name=_("Name"), max_length=100
    )
    state = models.ForeignKey(
        State,
        verbose_name=_("State"),
        on_delete=models.CASCADE,
        related_name="cities"
    )

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ["name"]

    def __str__(self):
        return self.name


class SiteInvite(models.Model):
    site = models.ForeignKey(
        "landplots.Site",
        on_delete=models.CASCADE,
        related_name="invites"
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    role = models.CharField(
        max_length=30,
        default="EMPLOYEE"
    )

    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        if self.is_used:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True