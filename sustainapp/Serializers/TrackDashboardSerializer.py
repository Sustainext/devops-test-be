from sustainapp.models import TrackDashboard
from rest_framework import serializers


class TrackDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackDashboard
        fields = ["report_name", "report_id", "group_id"]

    def to_representation(self, instance):
        # Override the representation to change the structure
        representation = super().to_representation(instance)

        return {
            representation["report_name"]: {
                "report_id": representation["report_id"],
                "group_id": representation["group_id"],
            }
        }
