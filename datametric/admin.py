from django.contrib import admin
from .models import MyModel, DataPoint, Path, FieldGroup, RawResponse, ResponsePoint


class MyModelAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")


admin.site.register(MyModel, MyModelAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")


class DataPointAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "label", "description", "response_type")


admin.site.register(DataPoint, DataPointAdmin)


class PathAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


admin.site.register(Path, PathAdmin)


class FieldGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "path", "meta_data", "ui_schema", "schema")


admin.site.register(FieldGroup, FieldGroupAdmin)


class RawResponseAdmin(admin.ModelAdmin):
    list_display = ("path", "created_at", "user", "client")


admin.site.register(RawResponse, RawResponseAdmin)


class ResponsePointAdmin(admin.ModelAdmin):
    list_display = (
        "path",
        "raw_response",
        "response_type",
        "value",
        "number_holder",
        "string_holder",
        "json_holder",
    )


admin.site.register(ResponsePoint, ResponsePointAdmin)
