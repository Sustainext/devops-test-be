from django.contrib import admin

# Register your models here.
# * Add all models in the admin panel

from django.contrib import admin
from materiality_dashboard.models import (
    ReportingPeriod,
    MaterialityAssessment,
    MaterialTopic,
    Disclosure,
    AssessmentTopicSelection,
    AssessmentDisclosureSelection,
    MaterialityChangeConfirmation,
    Stakeholder,
    MaterialityAssessmentProcess,
    ImpactType,
    MaterialityImpact,
    ManagementApproachQuestion,
)


@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date")
    search_fields = ("start_date", "end_date")


@admin.register(MaterialityAssessment)
class MaterialityAssessmentAdmin(admin.ModelAdmin):
    list_display = ("client", "organization", "reporting_period", "framework", "status")
    list_filter = ("status", "framework", "reporting_period")
    search_fields = ("client__name", "organization__name", "framework__name")
    readonly_fields = ("topic_summary", "disclosure_summary")


@admin.register(MaterialTopic)
class MaterialTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "framework")
    list_filter = ("framework",)
    search_fields = ("name",)


@admin.register(Disclosure)
class DisclosureAdmin(admin.ModelAdmin):
    list_display = ("topic", "description")
    search_fields = ("topic__name", "description")


@admin.register(AssessmentTopicSelection)
class AssessmentTopicSelectionAdmin(admin.ModelAdmin):
    list_display = ("assessment", "topic")
    search_fields = ("assessment__client__name", "topic__name")


@admin.register(AssessmentDisclosureSelection)
class AssessmentDisclosureSelectionAdmin(admin.ModelAdmin):
    list_display = ("topic_selection", "disclosure")
    search_fields = (
        "topic_selection__assessment__client__name",
        "disclosure__topic__name",
    )


@admin.register(MaterialityChangeConfirmation)
class MaterialityChangeConfirmationAdmin(admin.ModelAdmin):
    list_display = ("assessment", "change_made", "reason_for_change")
    search_fields = ("assessment__client__name",)
    list_filter = ("change_made",)


@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(MaterialityAssessmentProcess)
class MaterialityAssessmentProcessAdmin(admin.ModelAdmin):
    list_display = ("assessment",)
    search_fields = ("assessment__client__name",)
    filter_horizontal = ("selected_stakeholders",)


@admin.register(ImpactType)
class ImpactTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(MaterialityImpact)
class MaterialityImpactAdmin(admin.ModelAdmin):
    list_display = ("assessment", "material_topic", "impact_type")
    search_fields = (
        "assessment__client__name",
        "material_topic__name",
        "impact_type__name",
    )
    list_filter = ("impact_type",)


@admin.register(ManagementApproachQuestion)
class ManagementApproachQuestionAdmin(admin.ModelAdmin):
    list_display = ("assessment", "question_text")
    search_fields = ("assessment__client__name", "question_text")
