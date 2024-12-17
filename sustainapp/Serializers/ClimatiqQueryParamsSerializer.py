from rest_framework import serializers


class ClimatiqQueryParamsSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    category = serializers.CharField()
    region = serializers.CharField()

    class Meta:
        fields = ["year", "category", "region"]
