from django.contrib import admin
from .models import (
    MyModel,
    DataPoint,
    Path,
    FieldGroup,
    RawResponse,
    DataMetric,
    EmissionAnalysis,
)
from common.Mixins.ExportCsvMixin import ExportCsvMixin
from datametric.utils.CustomFieldGroupForm import FieldGroupAdminForm


class MyModelAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")


admin.site.register(MyModel, MyModelAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")


class DataMetricAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("id", "name", "path", "label", "description", "response_type")
    actions = ["export_as_csv"]


admin.site.register(DataMetric, DataMetricAdmin)


class PathAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("id", "name", "slug")
    actions = ["export_as_csv"]
    #* Add search fields
    search_fields = ["slug"]


admin.site.register(Path, PathAdmin)


class FieldGroupAdmin(admin.ModelAdmin):
    form = FieldGroupAdminForm
    list_display = ("id", "name", "path", "meta_data", "ui_schema", "schema")
    # * Add search functionality for path__slug field
    search_fields = ["path__slug"]


admin.site.register(FieldGroup, FieldGroupAdmin)


class RawResponseAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("id", "path", "created_at", "user", "client")
    actions = ["export_as_csv"]


admin.site.register(RawResponse, RawResponseAdmin)


class DataPointAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "path",
        "raw_response",
        "value",
        "metric_name",
        # "location",
        "year",
        "month",
    )


admin.site.register(DataPoint, DataPointAdmin)


class EmsissionAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "activity_id",
        "index",
        "co2e_total",
        "co2",
        "n2o",
        "co2e_other",
        "ch4",
        "calculation_method",
        "category",
        "region",
        "year",
        "name",
        "raw_response",
        "type_of",
    )
    list_filter = (
        "category",
        "region",
        "year",
        "raw_response__organization__name",
        "raw_response__corporate__name",
        "raw_response__client__name",
        "type_of",
    )


admin.site.register(EmissionAnalysis, EmsissionAnalysisAdmin)
