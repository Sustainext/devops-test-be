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
    AnalysisData2,
    TrackDashboard,
    CustomUser
)

from django.db import migrations
from django.db.models import Q


# Email push notification
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from authentication.Mixins.ClientAdminMixin import ClientFilterAdminMixin
from django.contrib.contenttypes.models import ContentType
from authentication.Views.CustomUserCreationForm import CustomUserCreationForm
from authentication.models import CustomUser, UserProfile
from authentication.admin import UserProfileInline
from authentication.AdminSite.ClientAdmin import client_admin_site,ClientAdmin

# from django.db.migrations.recorder import MigrationRecorder

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "customer"]


class User_clientAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "client"]


class OrganizationAdmin(ClientFilterAdminMixin, admin.ModelAdmin):
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


class CorporateentityAdmin(ClientFilterAdminMixin, admin.ModelAdmin):
    list_display = ["id", "name", "sector", "organization", "client"]
    list_filter = ("organization", "client")


class LocationAdmin(ClientFilterAdminMixin, admin.ModelAdmin):
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

    list_display = ["id", "user", "organization"]


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

class CustomUserAdmin(UserAdmin):
    print('customUserAdmin is hit here')
    model = CustomUser
    list_display = ['username', 'email', 'roles', 'client', 'custom_role', 'is_staff']
    list_filter = ('client', 'roles')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('roles', 'custom_role', 'is_client_admin', 'admin', 'client')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('roles', 'custom_role', 'is_client_admin', 'admin', 'client')}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client":
            kwargs["initial"] = Client.get_default_client()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.is_staff and request.user.client:
            return qs.filter(client=request.user.client)
        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            if 'client' in form.base_fields:
                form.base_fields['client'].queryset = Client.objects.filter(id=request.user.client.id)
            if 'client' in form.base_fields:
                form.base_fields['client'].initial = request.user.client
                form.base_fields['client'].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.client = request.user.client
        super().save_model(request, obj, form, change)
    
class AnnualReportAdmin(admin.ModelAdmin):
    list_display = ["client", "user"]
    list_filter = ("client", "user")


class IdentifyingInformationAdmin(admin.ModelAdmin):
    list_display = ["report_purpose_1", "user", "reporting_legal_name_2"]
    list_filter = ("client", "user")


class UserExtendedAdmin(ClientFilterAdminMixin, UserAdmin):
    add_form = CustomUserCreationForm  # Custom form for adding users

    # The default form for editing users remains unchanged (default UserAdmin behavior)
    list_display = ["username", "email", "client"]
    search_fields = ("username", "email", "client")
    ordering = ("username",)

    # The default fieldsets (for editing users)
    fieldsets = list(
        UserAdmin.fieldsets
    )  # Convert fieldsets to a list for modification

    # Add 'client' to a separate fieldset
    fieldsets.append((None, {"fields": ("client", "admin", "roles")}))

    # Modify the existing Permissions fieldset to include 'is_client_admin'
    for idx, fieldset in enumerate(fieldsets):
        if fieldset[0] == "Permissions":
            fieldsets[idx] = (
                fieldset[0],
                {
                    "fields": fieldset[1]["fields"]
                    + ("is_client_admin",)  # Add is_client_admin field
                },
            )

    # Convert fieldsets back to a tuple (Django expects fieldsets to be tuples)
    fieldsets = tuple(fieldsets)

    # Custom fieldsets for the Add User form only
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "admin",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    inlines = [
        UserProfileInline,
    ]

    def get_fieldsets(self, request, obj=None):
        """
        Returns different fieldsets depending on whether we're adding or editing a user.
        """
        if not obj:  # If adding a new user (obj is None)
            return self.add_fieldsets  # Return the custom fieldsets for adding a user

        # If editing a user, return the fieldsets for editing
        fieldsets = list(super().get_fieldsets(request, obj))

        # Remove whole permission fieldset if the user is not a superuser
        if not request.user.is_superuser:
            fieldsets = [
                fieldset for fieldset in fieldsets if fieldset[0] != "Permissions"
            ]

        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Return the correct form for adding or editing a user.
        """
        # Custom form for adding users
        if obj is None:  # If we're adding a new user (obj is None)
            form = self.add_form
        else:
            form = super().get_form(request, obj, **kwargs)

        if obj and obj.admin:
            if "roles" in form.base_fields:
                form.base_fields["roles"].disabled = True

        if request.user.is_superuser:
            return form

        # If the logged-in user is a client admin, restrict the client field
        if request.user.is_client_admin:
            # Filter the client field to only show the client's own data
            if "client" in form.base_fields:
                form.base_fields["client"].queryset = Client.objects.filter(
                    id=request.user.client_id
                )
                form.base_fields["client"].initial = request.user.client_id
                form.base_fields["client"].disabled = True

        return form

    def save_model(self, request, obj, form, change):
        """
        Override save_model to set the 'roles' field based on the 'admin' checkbox.
        """
        if obj.admin:
            obj.roles = "admin"  # Set role to admin if admin is checked

        # If the logged-in user is not a superuser, prevent them from changing the admin field
        if not (request.user.is_superuser or request.user.is_client_admin):
            obj.admin = form.initial.get(
                "admin", obj.admin
            )  # Restore the initial state of the admin field

        super().save_model(request, obj, form, change)


class ReportAdmin(admin.ModelAdmin):
    pass


class AnalysisReportDataAdmin(admin.ModelAdmin):
    pass


class ZohoInfoAdmin(admin.ModelAdmin):
    list_display = ["id", "client_name", "iframe_url", "table_no", "table_name"]
    list_filter = ("client__name",)
    search_fields = ("client__name", "table_no", "table_name")


class TrackDashboardAdmin(admin.ModelAdmin):
    list_display = ["id", "table_name", "report_name"]

class TrackDashboardAdmin(admin.ModelAdmin):
    list_display = ["id", "report_name"]

UserExtendedModel = apps.get_model(settings.AUTH_USER_MODEL)

admin.site.register(Regulation, RegulationAdmin),
admin.site.register(Report, ReportAdmin),
admin.site.register(AnalysisData2, AnalysisReportDataAdmin),
# admin.site.register(UserExtendedModel, UserExtendedAdmin),
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
admin.site.register(TrackDashboard, TrackDashboardAdmin),

# Clinet_admin site register
client_admin_site.register(CustomUser,CustomUserAdmin ),
client_admin_site.register(Organization, OrganizationAdmin),
client_admin_site.register(Corporateentity, CorporateentityAdmin),
client_admin_site.register(Location, LocationAdmin),
# client_admin_site.register(Client, ClientAdmin),

# client_admin_site.register(Client,ClientAdmin)

