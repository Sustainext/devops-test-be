from django.contrib import admin

# Register your models here.
from apps.tcfd_framework.report.models import TCFDReport


@admin.register(TCFDReport)
class ReportAdmin(admin.ModelAdmin):
    search_fields = ["report__organization__name"]
    list_display = ["id", "screen_name", "get_organization_name"]
    list_filter = ["screen_name"]

    def get_organization_name(self, obj):
        return (
            obj.report.organization.name
            if obj.report and obj.report.organization
            else None
        )

    get_organization_name.short_description = "Organization Name"