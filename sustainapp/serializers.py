from rest_framework import serializers
from sustainapp.models import (
    Organization,
    Corporateentity,
    Location,
    Stakeholdergroup,
    Stakeholder,
    Bussinessactivity,
    Task,
    Userorg,
    Category,
    Sector,
    Batch,
    RowDataBatch,
    Mygoal,
    TaskDashboard,
    Report,
    AnalysisData2,
    Client,
    User_client,
    Framework,
    Regulation,
    Target,
    Sdg,
    Certification,
    Rating,
)
import json
import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File
from rest_framework.exceptions import NotFound, ValidationError

# Loggers
logger = logging.getLogger()
warning_handler = logging.FileHandler("warning.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
warning_handler.setFormatter(formatter)
warning_handler.setLevel(logging.INFO)
logger.addHandler(warning_handler)


class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = "__all__"


class RegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = "__all__"


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = "__all__"


class SdgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sdg
        fields = "__all__"


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# class Userorg(serializers.ModelSerializer):
#     class Meta:
#         model = Userorg
#         fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class User_clientSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = User_client
        # fields="__all__"
        fields = ["client", "user", "user_name"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class LocationOrgstructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "phone",
            "mobile",
            "website",
            "fax",
            "employeecount",
            "revenue",
            "sector",
            "sub_industry",
            "streetaddress",
            "country",
            "state",
            "city",
            "zipcode",
            "dateformat",
            "currency",
            "timezone",
            "language",
            "corporateentity",
            "typelocation",
            "location_type",
            "area",
            "type_of_business_activities",
            "type_of_product",
            "type_of_services",
            "longitude",
            "latitude",
            "from_date",
            "to_date",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class CorporateentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporateentity
        fields = "__all__"

    def to_representation(self, instance):
        user = self.context["request"].user
        data = super().to_representation(instance)
        data["location"] = LocationSerializer(
            instance.location.filter(id__in=user.locs.all()), many=True
        ).data
        return data


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"

    def to_representation(self, instance):
        user = self.context["request"].user
        data = super().to_representation(instance)
        data["corporate"] = CorporateentitySerializer(
            instance.corporatenetityorg.filter(id__in=user.corps.all()).prefetch_related(
                "location"
            ),
            many=True,
            context={"request": self.context["request"]},
        ).data
        return data


class CorporateentityOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporateentity
        fields = "__all__"


class OrganizationOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class Task_display_emissionSerializer(serializers.ModelSerializer):
    uploadedBy = serializers.CharField(source="assigned_by.username")

    class Meta:
        model = Task
        fields = ["uploadedBy", "id"]


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ["id", "location", "year", "month", "total_co2e"]


def validate_filesize(value):
    filesize = value.size
    if filesize > 1024 * 1024 * 2:
        raise serializers.ValidationError("The maximum file size allowed is 2 MB")
    return value


class RowDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RowDataBatch
        fields = "__all__"

    def update(self, instance, validated_data):
        if (
            "file" in validated_data
            and validated_data["file"] != instance.file
            and len(instance.file) != 0
        ):
            instance.file.delete(save=False)
        return super(RowDataSerializer, self).update(instance, validated_data)


class RowDataBatchSerializer(serializers.ModelSerializer):
    task_rowdatabatch = Task_display_emissionSerializer(many=True)
    subCategory = serializers.CharField(source="category")
    category = serializers.CharField(source="sector")
    modifiedTime = serializers.DateTimeField(source="file_modified_at")
    unit = serializers.SerializerMethodField()
    unitType = serializers.CharField(source="unit_type")
    fileName = serializers.CharField(source="filename")
    assignTo = serializers.CharField(source="assign_to")

    class Meta:
        model = RowDataBatch
        fields = "__all__"

    def get_unit(self, obj):
        return [obj.unit1, obj.unit2]

    def update(self, instance, validated_data):
        instance.value1 = validated_data.get("value1", instance.value1)
        instance.save()
        return instance


class StakeholdergroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholdergroup
        fields = "__all__"


class StakeholderSerializer(serializers.ModelSerializer):
    stakeholdergroup_name = serializers.CharField(source="stakeholdergroup.name")

    class Meta:
        model = Stakeholder
        fields = "__all__"


class BussinessactivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bussinessactivity
        fields = "__all__"


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"


class MygoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mygoal
        fields = ["id", "title", "deadline", "assigned_to", "completed", "client"]


class TaskDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDashboard
        # fileds = ['id','taskname','deadline','assigned_to','completed']
        fields = "__all__"


class UserorgSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Userorg
        fields = [
            "id",
            "user",
            "designation",
            "department",
            "phone",
            "profile_picture",
            "first_name",
            "last_name",
        ]


class CustomRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(required=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), required=True
    )

    def custom_signup(self, request, user):
        first_name = self.validated_data.get("first_name")
        client_id = self.validated_data.get("client_id")
        user.first_name = first_name
        user.client = client_id
        user.save()

    def to_representation(self, instance):
        # Use the default representation provided by the parent class
        return super().to_representation(instance)


class ReportSerializer(serializers.ModelSerializer):
    organization_name = serializers.ReadOnlyField(source="organization.name")
    organization_country = serializers.ReadOnlyField(
        source="organization.countryoperation"
    )
    status = serializers.CharField(required=False)
    client = serializers.CharField(required=False)
    user = serializers.CharField(required=False)
    investment_corporates = serializers.JSONField(required=False)

    class Meta:
        model = Report
        fields = "__all__"


class ReportRetrieveSerializer(serializers.ModelSerializer):
    organization_name = serializers.ReadOnlyField(source="organization.name")
    organization_country = serializers.ReadOnlyField(
        source="organization.countryoperation"
    )
    corporate_name = serializers.ReadOnlyField(source="corporate.name")
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    last_updated_by = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "name",
            "report_type",
            "start_date",
            "end_date",
            "report_by",
            "organization_name",
            "corporate_name",
            "organization_country",
            "last_updated_by",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance: Report):
        # Override the to_representation method to filter data based on the status
        if (
            instance.status == 1
        ):  # Adjust the condition based on your status filtering requirement
            data = super().to_representation(instance)
            data["created_by"] = f"{instance.user.first_name} {instance.user.last_name}"
            return data
        else:
            return None

    def get_last_updated_by(self, obj):
        if obj.last_updated_by:
            first_name = obj.last_updated_by.first_name or ""
            last_name = obj.last_updated_by.last_name or ""
            return f"{first_name} {last_name}".strip()

    def get_created_at(self, obj):
        """Format created_at into '19 Nov 2024 10:40:45 am'."""
        if obj.created_at:
            return obj.created_at.strftime("%d %b %Y %I:%M:%S %p").lower()
        return None

    def get_updated_at(self, obj):
        """Format created_at into '19 Nov 2024 10:40:45 am'."""
        if obj.updated_at:
            return obj.updated_at.strftime("%d %b %Y %I:%M:%S %p").lower()
        return None


class ReportUpdateSerializer(serializers.ModelSerializer):
    org_logo = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = Report
        fields = [
            "about_the_organization",
            "roles_and_responsibilities",
            "organizational_boundries",
            "excluded_sources",
            "designation_of_organizational_admin",
            "reporting_period_name",
            "from_year",
            "to_year",
            "calender_year",
            "data_source",
            "org_logo",
        ]


class AnalysisData2Serializer(serializers.Serializer):
    report_id = serializers.CharField()
    data = serializers.JSONField()


class ScopeSerializerAnalysis(serializers.Serializer):
    scope_name = serializers.CharField()
    total_co2e = serializers.FloatField()
    contribution_scope = serializers.FloatField()


class LocationSerializerAnalysis(serializers.Serializer):
    location_name = serializers.CharField()
    location_address = serializers.CharField()
    total_co2e = serializers.FloatField()
    contribution_location = serializers.FloatField()


class SourceSerializerAnalysis(serializers.Serializer):
    source_name = serializers.CharField()
    category_name = serializers.CharField()
    total_co2e = serializers.FloatField()
    contribution_source = serializers.FloatField()


class CorporateSerializerAnalysis(serializers.Serializer):
    corporate_name = serializers.CharField()
    scopes = ScopeSerializerAnalysis(many=True)
    locations = LocationSerializerAnalysis(many=True)
    sources = SourceSerializerAnalysis(many=True)


class AnalysisDataResponseSerializer(serializers.Serializer):
    # report_id = serializers.CharField()
    data = serializers.ListField(child=serializers.DictField())


class OrglogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["org_logo"]

    def create(self, validated_data):
        org_logo = validated_data.pop("org_logo", None)
        instance = super(OrglogoSerializer, self).create(validated_data)

        if org_logo:
            instance.org_logo = org_logo
            instance.save()

        return instance

    def update(self, instance, validated_data):
        org_logo = validated_data.pop("org_logo", None)
        instance = super(OrglogoSerializer, self).update(instance, validated_data)

        if org_logo:
            instance.org_logo = org_logo
            instance.save()

        return instance


"""Serializers for Annual Report from Canada Bill S211"""


# Serializer for Screen 1
