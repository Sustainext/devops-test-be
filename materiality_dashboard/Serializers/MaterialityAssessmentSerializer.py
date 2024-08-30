from rest_framework import serializers
from materiality_dashboard.models import MaterialityAssessment, AssessmentTopicSelection


class MaterialityAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialityAssessment
        fields = [
            "id",
            "organization",
            "corporate",
            "start_date",
            "end_date",
            "framework",
            "approach",
            "status",
        ]
        read_only_fields = ["client"]

    def to_representation(self, instance: MaterialityAssessment):
        data = super().to_representation(instance)
        data["organisation_name"] = instance.organization.name
        data["corporate_name"] = instance.corporate.name if instance.corporate else None
        return data


class MaterialityAssessmentGetSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name")
    corporate_name = serializers.CharField(
        source="corporate.name", allow_null=True, required=False
    )
    framework_name = serializers.CharField(source="framework.name")
    environment_topics = serializers.SerializerMethodField()
    social_topics = serializers.SerializerMethodField()
    governance_topics = serializers.SerializerMethodField()

    class Meta:
        model = MaterialityAssessment
        fields = [
            "id",
            "organization_name",
            "corporate_name",
            "framework_name",
            "start_date",
            "end_date",
            "status",
            "environment_topics",
            "social_topics",
            "governance_topics",
        ]

    def get_environment_topics(self, obj):
        return self._get_topics_by_category(obj, "environmental")

    def get_social_topics(self, obj):
        return self._get_topics_by_category(obj, "social")

    def get_governance_topics(self, obj):
        return self._get_topics_by_category(obj, "governance")

    def _get_topics_by_category(self, obj, category):
        topic_selections = AssessmentTopicSelection.objects.filter(
            assessment=obj, topic__esg_category=category
        ).select_related("topic")
        topics = [selection.topic.name for selection in topic_selections]
        return topics if topics else "Not Selected"
