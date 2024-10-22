from rest_framework import serializers
from authentication.models import CustomUser
from sustainapp.models import Organization, Corporateentity, Location


# Serializer for Org model
class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name"]


# Serializer for Corp model
class CorpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporateentity
        fields = ["id", "name"]


# Serializer for Loc model
class LocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name"]


class ManageUserSerializer(serializers.ModelSerializer):
    # Accept IDs for the related fields (organizations, corporations, and locations)
    orgs = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Organization.objects.all()
    )
    corps = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Corporateentity.objects.all()
    )
    locs = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Location.objects.all()
    )

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
            "permissions_checkbox",
            "collect",
            "analyse",
            "report",
            "optimise",
            "track",
            "orgs",
            "corps",
            "locs",
        ]

    def to_representation(self, instance):
        # Get the standard representation
        representation = super().to_representation(instance)

        # Customize representation for orgs, corps, and locs to include both id and name
        representation["orgs"] = [
            {"id": org.id, "name": org.name} for org in instance.orgs.all()
        ]
        representation["corps"] = [
            {"id": corp.id, "name": corp.name} for corp in instance.corps.all()
        ]
        representation["locs"] = [
            {"id": loc.id, "name": loc.name} for loc in instance.locs.all()
        ]

        return representation

    def update(self, instance, validated_data):
        # Handle related fields (orgs, corps, locs) update
        orgs = validated_data.pop("orgs", None)
        corps = validated_data.pop("corps", None)
        locs = validated_data.pop("locs", None)

        # Update other fields
        instance = super().update(instance, validated_data)

        # Update many-to-many relationships if the data is present
        if orgs is not None:
            instance.orgs.set(orgs)
        if corps is not None:
            instance.corps.set(corps)
        if locs is not None:
            instance.locs.set(locs)

        return instance
