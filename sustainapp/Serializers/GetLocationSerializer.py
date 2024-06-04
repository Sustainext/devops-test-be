from sustainapp.models import Location
from rest_framework.serializers import ModelSerializer


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name"]
