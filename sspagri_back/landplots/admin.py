from django.contrib import admin
from .models import PlantSpecies, Site, Cultivation, CultivationPlant, SiteMembership, Task

@admin.register(PlantSpecies)
class PlantSpeciesAdmin(admin.ModelAdmin):
    list_display = ("name", "life_cycle", "germination", "flowering", "fructification")

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country", "number", "timezone")
    search_fields  = ("name",)
    list_filter    = ("country",)

@admin.register(Cultivation)
class CultivationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "site", "quantity")
    list_filter  = ("site",)

@admin.register(CultivationPlant)
class CultivationPlantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cultivation",
        "plant_species",
        "planting_day",
        "harvest_day",
        "count",
    )
    list_filter  = ("plant_species", "cultivation")

@admin.register(SiteMembership)
class SiteMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "site", "user", "role")
    list_filter  = ("role",)

@admin.register(Task)
class TasksAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "start_in", "end_in")
    filter_horizontal = ("cultivation",)