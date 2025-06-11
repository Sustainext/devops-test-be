from django.contrib import admin
from apps.tcfd_framework.models.TCFDCollectModels import (
    CoreElements,
    RecommendedDisclosures,
    DataCollectionScreen,
)


@admin.register(CoreElements)
class CoreElementsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(RecommendedDisclosures)
class RecommendedDisclosuresAdmin(admin.ModelAdmin):
    list_display = ("description", "core_element", "screen_tag")
    search_fields = ("core_element__name", "screen_tag")


@admin.register(DataCollectionScreen)
class DataCollectionScreenAdmin(admin.ModelAdmin):
    list_display = ("name", "get_recommended_disclosure")
    search_fields = ("name", "recommended_disclosure__description")

    def get_recommended_disclosure(self, obj):
        return obj.recommended_disclosure.description[:50]

    get_recommended_disclosure.short_description = "Recommended Disclosure"
