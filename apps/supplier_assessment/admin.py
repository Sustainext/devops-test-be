from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import StakeHolder, StakeHolderGroup


class StakeHolderGroupAdmin(SimpleHistoryAdmin):
    # Display these fields in the list view
    list_display = ("name", "group_type", "organization", "created_by")

    # Add search fields for easy searching
    search_fields = ("name", "group_type", "organization__name", "created_by__username")

    # Add filters for filtering the list view
    list_filter = ("group_type", "organization", "created_by")

    # Add a filter horizontal for ManyToManyField (corporate_entity)
    filter_horizontal = ("corporate_entity",)

    # Add a fieldset for better organization in the add/edit form
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "group_type",
                    "organization",
                    "corporate_entity",
                    "created_by",
                )
            },
        ),
    )


class StakeHolderAdmin(SimpleHistoryAdmin):
    # Display these fields in the list view
    list_display = ("id", "name", "group", "email", "poc")

    # Add search fields for easy searching
    search_fields = ("name", "email", "group__name", "poc")

    # Add filters for filtering the list view
    list_filter = ("group", "group__group_type", "group__organization")

    # Add a fieldset for better organization in the add/edit form
    fieldsets = ((None, {"fields": ("name", "group", "email", "poc")}),)


# Register the models with their respective admin classes
admin.site.register(StakeHolderGroup, StakeHolderGroupAdmin)
admin.site.register(StakeHolder, StakeHolderAdmin)
