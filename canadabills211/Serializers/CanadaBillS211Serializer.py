from rest_framework import serializers
from canadabills211.models.CanadaBillS211 import (
    IdentifyingInformation,
)
from sustainapp.models import Organization, Corporateentity

"""Serializers of Identifying Information in Canada Bill S-211, II ==> Identifying_Information"""


class IISerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentifyingInformation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        # Dynamically select fields based on screen parameter
        screen_number = kwargs.pop("screen_number", None)
        super().__init__(*args, **kwargs)

        # Define screen-specific fields
        screen_fields_mapping = {
            "1": [
                "organization_id",
                "corporate_id",
                "year",
                "user_id",
                "report_purpose_1",
                "reporting_legal_name_2",
                "financial_reporting_year_from_3",
                "financial_reporting_year_to_3",
            ],
            "2": [
                "organization_id",
                "corporate_id",
                "year",
                "user_id",
                "is_revised_version_4",
                "original_report_date_4_1",
                "changes_description_4_2",
            ],
            "3": [
                "organization_id",
                "corporate_id",
                "year",
                "user_id",
                "business_number_5",
                "is_joint_report_6",
                "legal_name_and_business_numbers_6_1_2",
            ],
            "4": [
                "organization_id",
                "corporate_id",
                "year",
                "user_id",
                "subject_to_supply_chain_legislation_7",
                "applicable_laws_7_1",
                "other_laws_description_7_1",
            ],
            "5": [
                "organization_id",
                "corporate_id",
                "year",
                "user_id",
                "categorizations_8",
            ],
            "6": [
                "organization_id",
                "corporate_id",
                "year",
                "user_id",
                "sectors_or_industries_9",
                "sectors_or_industries_description_9",
            ],
            "7": [
                "organization_id",
                "corporate_id",
                "year",
                "user_id",
                "country_10",
                "province_or_territory_10_1",
            ],
        }

        # Adjust fields dynamically
        if screen_number and screen_number in screen_fields_mapping:
            self.fields = {
                field: self.fields.get(field)
                for field in screen_fields_mapping[screen_number]
                if field in self.fields
            }
        elif screen_number:
            raise serializers.ValidationError(
                {"error": f"Invalid screen number: {screen_number}"}
            )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Replace None with empty strings for specific fields
        for field, value in data.items():
            if value is None:
                data[field] = ""
        return data

    def create(self, validated_data):
        organization_id = self.initial_data.get("organization_id")
        corporate_id = self.initial_data.get("corporate_id")
        user_id = self.initial_data.get("user_id")
        year = self.initial_data.get("year")

        if not organization_id or not year:
            raise serializers.ValidationError(
                {"organization_id and Year are required."}
            )
        if corporate_id:
            try:
                corporate_entity = Corporateentity.objects.get(
                    id=corporate_id, organization_id=organization_id
                )
            except Exception as e:
                raise serializers.ValidationError(
                    {
                        "error": f"Corporate entity not found for the given organization_id {organization_id} and corporate_id {corporate_id}",
                        "exception": f"{e}",
                    }
                )
        # Convert organization_id to an instance
        validated_data["user_id"] = user_id
        validated_data["organization_id"] = organization_id
        validated_data["corporate_id"] = corporate_id
        return super().create(validated_data)
