from sustainapp.models import TrackDashboard
from rest_framework import serializers

class TrackDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackDashboard
        fields = ['client_id','report_name','report_id','group_id']

    def to_representation(self, instance):
        # Override the representation to change the structure
        representation = super().to_representation(instance)
        
        # Return the desired structure: {report_name: {report_id, group_id}}
        return {
            representation['report_name']: {
                'report_id': representation['report_id'],
                'group_id': representation['group_id'],
            }
        }