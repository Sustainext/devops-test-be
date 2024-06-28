from django.contrib import admin
from .models import MyModel, DataPoint, Path, FieldGroup, RawResponse, DataMetric
from common.Mixins.ExportCsvMixin import ExportCsvMixin


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


admin.site.register(Path, PathAdmin)


class FieldGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "path", "meta_data", "ui_schema", "schema")


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
        "location",
        "year",
        "month",
    )


admin.site.register(DataPoint, DataPointAdmin)
