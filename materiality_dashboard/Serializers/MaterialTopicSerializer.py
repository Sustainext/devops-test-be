from rest_framework import serializers
from materiality_dashboard.models import MaterialTopic
from sustainapp.models import Framework


class MaterialTopicModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialTopic
        exclude = ["created_at", "updated_at"]


# * Create a custom serializer that checks if the framework is selected or not
class CustomFrameworkSerializer(serializers.Serializer):
    framework_id = serializers.PrimaryKeyRelatedField(
        queryset=Framework.objects.all(), required=True
    )

    class Meta:
        fields = ["framework_id"]
