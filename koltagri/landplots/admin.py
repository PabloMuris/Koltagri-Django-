from django.contrib import admin
from django.contrib.gis import admin as gis_admin # Importante para os campos de geometria
from .models import (
    ClimateZone,
    PlantSpecies,
    Site,
    Cultivation,
    CultivationPlant,
    PlantingEvent,
    SiteMembership
)

@admin.register(ClimateZone)
class ClimateZoneAdmin(admin.ModelAdmin):
    list_display = ('code', '__str__')
    search_fields = ('code',)


@admin.register(PlantSpecies)
class PlantSpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'life_cycle', 'germination', 'flowering', 'fructification')
    list_filter = ('life_cycle',)
    search_fields = ('name',)
    filter_horizontal = ('climate_zones',) # Melhora a seleção de ManyToMany


class SiteMembershipInline(admin.TabularInline):
    model = SiteMembership
    extra = 1
    autocomplete_fields = ['user', 'role'] # Requer que User e Group tenham search_fields configurados


@admin.register(Site)
class SiteAdmin(gis_admin.GISModelAdmin): # Usa GISModelAdmin para o mapa
    list_display = ('name', 'country', 'timezone')
    list_filter = ('country', 'timezone')
    search_fields = ('name', 'country__name')
    inlines = [SiteMembershipInline]
    
    # Configurações opcionais do mapa GIS
    # openlayers_url = '...' 


@admin.register(SiteMembership)
class SiteMembershipAdmin(admin.ModelAdmin):
    list_display = ('site', 'user', 'role')
    list_filter = ('role', 'site')
    search_fields = ('user__username', 'user__email', 'site__name')
    autocomplete_fields = ['site', 'user', 'role']


class CultivationPlantInline(admin.TabularInline):
    model = CultivationPlant
    extra = 0


@admin.register(Cultivation)
class CultivationAdmin(admin.ModelAdmin): # Usa GISModelAdmin para o mapa
    list_display = ('name', 'site', 'id')
    list_filter = ('site',)
    search_fields = ('name', 'site__name')
    inlines = [CultivationPlantInline]


@admin.register(CultivationPlant)
class CultivationPlantAdmin(admin.ModelAdmin):
    list_display = ('cultivation', 'plant_species', 'count', 'new_plantation')
    list_filter = ('new_plantation', 'plant_species', 'cultivation__site')
    search_fields = ('cultivation__name', 'plant_species__name')


@admin.register(PlantingEvent)
class PlantingEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_date', 'cultivation_plant_info')
    list_filter = ('event_type', 'event_date')
    search_fields = ('notes', 'cultivation_plant__cultivation__name')
    date_hierarchy = 'event_date'

    def cultivation_plant_info(self, obj):
        return str(obj.cultivation_plant)
    cultivation_plant_info.short_description = "Plantio"