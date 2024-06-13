from django.contrib import admin
from django.conf import settings
from django.apps import apps
from sustainapp.models import (
    Organization,
    Corporateentity,
    Location,
    Sdg,
    Rating,
    Framework,
    Certification,
    Target,
    Stakeholdergroup,
    Bussinessactivity,
    Bussinessrelationship,
    Sector,
    Source,
    Category,
    Task,
    Userorg,
    Companyactivities,
    Scope,
    RowDataBatch,
    Batch,
    Mygoal,
    TaskDashboard,
    User_client,
    Client,
    ClientTaskDashboard,
    Framework,
    Report,
    Regulation,
    Target,
    Sdg,
    Certification,
    ZohoInfo,
    LoginCounter,
    AnalysisData2,
)

from django.db import migrations


# Email push notification
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# from django.db.migrations.recorder import MigrationRecorder

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "customer"]


class User_clientAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "client"]


class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "client",
        "owner",
        "countryoperation",
        "employeecount",
        "website",
        "active",
    ]
    list_filter = ("client",)


class CorporateentityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "sector", "organization", "client"]
    list_filter = ("organization", "client")


class LocationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "corporateentity",
        "employeecount",
        "sector",
        "client",
    ]
    list_filter = ("corporateentity__organization", "corporateentity", "client")


class UserorgAdmin(admin.ModelAdmin):

    list_display = ["id", "user_id", "organization_id"]


class SdgAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "Image", "Target_no", "goal_no"]


class RatingAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "Image"]


class FrameworkAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "Image"]


class CertificationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "Image"]


class TargetAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "Image"]


class RegulationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "Image"]


class StakeholdergroupAdmin(admin.ModelAdmin):
    pass


class BussinessrelationshipAdmin(admin.ModelAdmin):
    pass


class BussinessactivityAdmin(admin.ModelAdmin):
    pass


class relationshipAdmin(admin.ModelAdmin):
    pass


class SectorAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


class SourceAdmin(admin.ModelAdmin):
    pass


# class relationshipAdmin(admin.ModelAdmin):
#     pass


class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "row_data_batch"]


class MigrationsAdmin(admin.ModelAdmin):
    pass


class ScopeAdmin(admin.ModelAdmin):
    pass


class CompanyactivitiesAdmin(admin.ModelAdmin):
    pass


class RowDataBatchAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "scope",
        "co2e",
        "row_number",
        "sector",
        "batch",
        "category",
        "unit_type",
    ]
    list_filter = (
        "client",
        "batch__year",
        "batch",
        "batch__location__corporateentity__organization__client",
        "batch__location__corporateentity__organization",
        "batch__location__corporateentity",
        "batch__location",
        "scope",
        "category",
        "sector",
    )


class BatchAdmin(admin.ModelAdmin):
    list_display = ["id", "location", "year", "month", "total_co2e"]
    list_filter = (
        "client",
        "location",
        "year",
        "month",
        "location__corporateentity",
        "location__corporateentity__organization",
        "location__corporateentity__organization__client",
    )


class MygoalAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "deadline", "assigned_to", "completed"]
    list_filter = ("assigned_to", "completed", "deadline")


class TaskDashboardAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "taskname",
        "deadline",
        "client_id",
        "assigned_to",
        "completed",
    ]


class ClientTaskDashboardAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "task_name",
        "location",
        "assigned_to",
        "created_at",
        "deadline",
        "task_status",
    ]


# class CustomUserAdmin(BaseUserAdmin):
#     # Add fieldsets for adding user
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
#         }),
#     )


class AnnualReportAdmin(admin.ModelAdmin):
    list_display = ["client", "user"]
    list_filter = ("client", "user")


class IdentifyingInformationAdmin(admin.ModelAdmin):
    list_display = ["report_purpose_1", "user", "reporting_legal_name_2"]
    list_filter = ("client", "user")


class UserExtendedAdmin(UserAdmin):
    list_display = ["username", "client"]
    list_filter = ("client",)
    search_fields = ("username", "email", "client")
    ordering = ("username",)
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("client",)}),)


class ReportAdmin(admin.ModelAdmin):
    pass


class AnalysisReportDataAdmin(admin.ModelAdmin):
    pass


class ZohoInfoAdmin(admin.ModelAdmin):
    list_display = ["id", "client_name", "iframe_url", "table_no", "table_name"]
    list_filter = ("client__name",)
    search_fields = ("client__name", "table_no", "table_name")


class LoginCounterAdmin(admin.ModelAdmin):
    list_display = ["login_counter", "user"]
    list_filter = ("user",)
    search_fields = ("user",)


UserExtendedModel = apps.get_model(settings.AUTH_USER_MODEL)

admin.site.register(Regulation, RegulationAdmin),
admin.site.register(Report, ReportAdmin),
admin.site.register(AnalysisData2, AnalysisReportDataAdmin),
admin.site.register(UserExtendedModel, UserExtendedAdmin),
admin.site.register(Batch, BatchAdmin),
admin.site.register(Client, ClientAdmin),
admin.site.register(User_client, User_clientAdmin),
admin.site.register(RowDataBatch, RowDataBatchAdmin),
admin.site.register(Companyactivities, CompanyactivitiesAdmin),
admin.site.register(Scope, ScopeAdmin),
admin.site.register(Task, TaskAdmin),
admin.site.register(Sector, SectorAdmin),
admin.site.register(Category, CategoryAdmin),
admin.site.register(Source, SourceAdmin),
admin.site.register(Bussinessrelationship, BussinessrelationshipAdmin),
admin.site.register(Stakeholdergroup, StakeholdergroupAdmin),
admin.site.register(Organization, OrganizationAdmin),
admin.site.register(Corporateentity, CorporateentityAdmin),
admin.site.register(Location, LocationAdmin),
admin.site.register(Sdg, SdgAdmin),
admin.site.register(Rating, RatingAdmin),
admin.site.register(Framework, FrameworkAdmin),
admin.site.register(Certification, CertificationAdmin),
admin.site.register(Target, TargetAdmin),
admin.site.register(Userorg, UserorgAdmin),
admin.site.register(Mygoal, MygoalAdmin),
admin.site.register(TaskDashboard, TaskDashboardAdmin),
admin.site.register(ClientTaskDashboard, ClientTaskDashboardAdmin),
admin.site.register(ZohoInfo, ZohoInfoAdmin),
admin.site.register(LoginCounter, LoginCounterAdmin),
