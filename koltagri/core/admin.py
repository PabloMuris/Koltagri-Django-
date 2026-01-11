from django.contrib import admin

# Register your models here.

from .models import Country, State, City

class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
    list_filter = ("country",)

class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state")
    search_fields = ("name",)
    list_filter = ("state",)

admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
