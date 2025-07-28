import zoneinfo

from django.db import models

from django.conf import settings
from django.contrib.gis.db import models as geomodels

from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError


from django.contrib.auth.models import Group

from .choices import KoppenClimate
from sspagri_back.core.models import BaseModel,BaseModelWithSoftDelete
import sspagri_back.person.models as person_models
from .manager import SiteMembershipActiveUsersManager

from sspagri_back.core.constants import (
    SMALL_CHAR_FIELD_NAME_LENGTH,
    MEDIUM_CHAR_FIELD_NAME_LENGTH,
    MAX_CHAR_FIELD_NAME_LENGTH,
    ROLE_SITE_OWNER,
    ROLE_SITE_MANAGER,
    ROLE_STUDY_TEAM,
    ROLE_STUDY_MANAGER,
)

class ClimateZone(models.Model):
    code = models.CharField(
        max_length=3,
        choices=KoppenClimate.choices,
        unique=True
    )

    def __str__(self):
        return self.get_code_display()


class PlantSpecies(BaseModelWithSoftDelete):
    class LifeCycle(models.TextChoices):
        PERENNIAL = "perennial", _("Perene")
        ANNUAL = "annual", _("Anual")
        BIENNIAL = "biennial", _("Bianual")

    name = models.CharField(max_length=100)
    life_cycle = models.CharField(
        max_length=10,
        choices=LifeCycle.choices,
        default=LifeCycle.PERENNIAL,
    )

    germination = models.PositiveIntegerField(help_text="Dias médios até a germinação")
    flowering = models.PositiveIntegerField()
    fructification = models.PositiveIntegerField()
    precipitation_needs = models.PositiveIntegerField()
    climate_zones = models.ManyToManyField(ClimateZone)


class Site(BaseModel):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        "core.Country",
        verbose_name="Country",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="SiteMembership",
        through_fields=("site", "user"),
    )
    timezone = models.CharField(default="UTC", max_length=50)
    area = geomodels.MultiPolygonField(null=True, blank=True)

    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        constraints = [
            models.UniqueConstraint(
                name="unique_name", fields=["name"]
            ),
        ]

    def clean(self):
        super_clean = super().clean()
        if self.timezone not in zoneinfo.available_timezones():
            raise ValidationError({"timezone": "Invalid timezone"})
        return super_clean

    def save(self, **kwargs):
        self.clean()
        return super().save(**kwargs)

    def __str__(self):
        return f"{self.pk} | {self.name}"


class Cultivation(BaseModelWithSoftDelete):
    name = models.CharField(max_length=100)
    area = geomodels.MultiPolygonField(null=True, blank=True)
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="cultivations"
    )
    quantity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.site.name})"


class CultivationPlant(BaseModelWithSoftDelete):
    cultivation = models.ForeignKey(
        Cultivation,
        on_delete=models.CASCADE,
        related_name="plants"
    )
    plant_species = models.ForeignKey(
        PlantSpecies,
        on_delete=models.CASCADE,
        related_name="plantings"
    )
    area = geomodels.MultiPolygonField(null=True, blank=True)
    planting_day = models.DateField()
    harvest_day = models.DateField()
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return (f"{self.count} x {self.plant_species.name} in "
                f"{self.cultivation.name}: {self.planting_day} -> {self.harvest_day}")
    
    def clean(self):
        super().clean()

        if self.harvest_day<self.planting_day:
            raise ValidationError({
                'harvest_day': 'The harvest day can\'t the same day as planting day'
            })
        

class SiteMembership(BaseModel):
    site = models.ForeignKey("Site", verbose_name=_("Site"), on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE
    )
    role = models.ForeignKey(Group, on_delete=models.CASCADE)

    objects = models.Manager()
    actives = SiteMembershipActiveUsersManager()

    def clean(self):
        allowed_groups = {
            ROLE_SITE_OWNER,
            ROLE_SITE_MANAGER,
            ROLE_STUDY_TEAM,
            ROLE_STUDY_MANAGER,
        }
        if self.role.name not in allowed_groups:
            raise ValidationError({
                'role': _(
                    f"O grupo “{self.role.name}” não é um papel permitido para SiteMembership."
                )
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


    class Meta:
        constraints = [
            models.UniqueConstraint(name="unique_user_site", fields=["user", "site"]),
        ]


class Task(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cultivation_plant= models.ManyToManyField(CultivationPlant, verbose_name=_(""))
    start_in = models.DateTimeField()
    end_in = models.DateTimeField()