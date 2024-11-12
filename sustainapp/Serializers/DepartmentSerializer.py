from rest_framework import serializers
from sustainapp.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]  # Exclude 'client' from fields

