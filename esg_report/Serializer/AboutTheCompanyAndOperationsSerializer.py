from rest_framework import serializers
from esg_report.models.ScreenTwo import AboutTheCompanyAndOperations



class AboutTheCompanyAndOperationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutTheCompanyAndOperations
        fields = "__all__"
