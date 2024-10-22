from authentication.models import CustomUser
from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity, Location


# Serializer for Org model
class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization  # Assuming your model for Orgs is called Org
        fields = ["id", "name"]


# Serializer for Corp model
class CorpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporateentity  # Assuming your model for Corps is called Corp
        fields = ["id", "name"]


# Serializer for Loc model
class LocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location  # Assuming your model for Locs is called Loc
        fields = ["id", "name"]


class ManageUserSerializer(serializers.ModelSerializer):
    orgs = OrgSerializer(many=True, read_only=True)
    corps = CorpSerializer(many=True, read_only=True)
    locs = LocSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "is_active",
            "roles",
            "first_name",
            "last_name",
            "date_joined",
            "phone_number",
            "job_title",
            "department",
            "work_email",
            "collect",
            "analyse",
            "report",
            "optimise",
            "track",
            "orgs",
            "corps",
            "locs",
        ]
