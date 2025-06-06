
from django.contrib import admin
from .models import Country, State, City


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ['country_name', 'sortname', 'slug']
    list_filter = ['sortname']
    list_display = ['country_name', 'sortname', 'slug']

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['state_name', 'country']
    list_filter = ['country']
    search_fields = ['state_name']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['city_name', 'state']
    list_filter = ['state']
    search_fields = ['city_name']

