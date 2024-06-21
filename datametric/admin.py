from django.contrib import admin
from .models import MyModel, DataPoint, Path, FieldGroup, RawResponse, DataMetric


class MyModelAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")


admin.site.register(MyModel, MyModelAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ("id","name", "created_at")


class DataMetricAdmin(admin.ModelAdmin):
    list_display = ("id","name","path", "label", "description", "response_type")


admin.site.register(DataMetric, DataMetricAdmin)


class PathAdmin(admin.ModelAdmin):
    list_display = ("id","name", "slug")


admin.site.register(Path, PathAdmin)


class FieldGroupAdmin(admin.ModelAdmin):
    list_display = ("id","name", "path", "meta_data", "ui_schema", "schema")


admin.site.register(FieldGroup, FieldGroupAdmin)


class RawResponseAdmin(admin.ModelAdmin):
    list_display = ("id","path", "location","year","month", "user", "client")


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
