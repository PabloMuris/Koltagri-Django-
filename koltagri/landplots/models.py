import zoneinfo

from django.db import models

from django.conf import settings
from django.contrib.gis.db import models as geomodels

from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError


from django.contrib.auth.models import Group

from .choices import KoppenClimate
from koltagri.core.models import BaseModel,BaseModelWithSoftDelete
import koltagri.person.models as person_models
from .manager import SiteMembershipActiveUsersManager

from koltagri.core.constants import (
    SMALL_CHAR_FIELD_NAME_LENGTH,
    MEDIUM_CHAR_FIELD_NAME_LENGTH,
    MAX_CHAR_FIELD_NAME_LENGTH,
    ROLE_SITE_OWNER,
    ROLE_SITE_MANAGER,
    ROLE_STUDY_TEAM,
    ROLE_STUDY_MANAGER,
    ROLE_EMPLOYEE,
    ROLE_TECNICAL_ASSISTANCE,
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

    class LuminosityNeeds(models.TextChoices):
        FULL_SUN = "full_sun", _("Sol Pleno")
        PARTIAL_SHADE = "partial_shade", _("Meia Sombra")
        FULL_SHADE = "full_shade", _("Sombra Total")

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
    luminosity_needs = models.CharField(
        max_length=15,
        choices=LuminosityNeeds.choices,
        default=LuminosityNeeds.PARTIAL_SHADE,
    )


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
    count = models.PositiveIntegerField(default=1)
    new_plantation = models.BooleanField(default=True)

    def __str__(self):
        return (f"{self.count} x {self.plant_species.name} in "
                f"{self.cultivation.name}: {self.pk}")
    
    

class PlantingEvent(BaseModel):
    class EventType(models.TextChoices):
        THINNING = "thinning", _("Desbaste")
        PRUNING = "pruning", _("Poda")
        POLLINATION = "pollination", _("Polinização")
        FERTILIZATION = "fertilization", _("Fertilização")
        PEST_CONTROL = "pest_control", _("Controle de Pragas")
        

    
    cultivation_plant = models.ForeignKey(
        CultivationPlant,
        on_delete=models.CASCADE,
        related_name="events",  
        verbose_name=_("Plantio")
    )
    
    
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        verbose_name=_("Tipo de Evento")
    )
    
    event_date = models.DateField(
        verbose_name=_("Data do Evento")
    )
    
    # Um campo opcional para notas
    notes = models.TextField(
        null=True, 
        blank=True, 
        verbose_name=_("Anotações")
    )

    def __str__(self):
        return f"{self.get_event_type_display()} em {self.event_date} para {self.cultivation_plant.id}"

    class Meta:
        verbose_name = _("Evento de Plantio")
        verbose_name_plural = _("Eventos de Plantio")
        ordering = ['event_date'] # Ordenar eventos por data


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
            ROLE_EMPLOYEE,
            ROLE_TECNICAL_ASSISTANCE,
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


