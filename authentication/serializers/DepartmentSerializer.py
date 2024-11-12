from rest_framework import serializers
from authentication.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "value"]  # Exclude 'client' from fields

