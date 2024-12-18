from rest_framework import serializers
from canadabills211.models.CanadaBillS211 import IdentifyingInformation, AnnualReport
from sustainapp.models import Organization, Corporateentity


class BaseDynamicScreenSerializer(serializers.ModelSerializer):
    """
    Base serializer with dynamic field selection based on the screen number.
    """

    screen_fields_mapping = {}  # Override this in subclasses

    def __init__(self, *args, **kwargs):
        screen_number = kwargs.pop("screen_number", None)
        super().__init__(*args, **kwargs)

        # Dynamically select fields based on screen number
        if screen_number and screen_number in self.screen_fields_mapping:
            self.fields = {
                field: self.fields.get(field)
                for field in self.screen_fields_mapping[screen_number]
                if field in self.fields
            }
        elif screen_number:
            raise serializers.ValidationError(
                {"error": f"Invalid screen number: {screen_number}"}
            )

    def to_representation(self, instance):
        """
        Replace None values with empty strings in the representation.
        """
        data = super().to_representation(instance)
        for field, value in data.items():
            if value is None:
                data[field] = ""
        return data

    def create(self, validated_data):
        """
        Shared creation logic for serializers.
        """
        organization_id = self.initial_data.get("organization_id")
        corporate_id = self.initial_data.get("corporate_id")
        user_id = self.initial_data.get("user_id")
        year = self.initial_data.get("year")
        client = self.initial_data.get("client_id")
        if not organization_id or not year:
            raise serializers.ValidationError(
                {"error": "organization_id and Year are required."}
            )
        if corporate_id:
            try:
                Corporateentity.objects.get(
                    id=corporate_id, organization_id=organization_id
                )
            except Exception as e:
                raise serializers.ValidationError(
                    {
                        "error": f"Corporate entity not found for organization_id={organization_id} and corporate_id={corporate_id}",
                        "exception": str(e),
                    }
                )

        validated_data["user_id"] = user_id
        validated_data["organization_id"] = organization_id
        validated_data["corporate_id"] = corporate_id
        validated_data["client_id"] = client
        return super().create(validated_data)


class IISerializer(BaseDynamicScreenSerializer):
    """
    Serializer for Identifying Information.
    """

    class Meta:
        model = IdentifyingInformation
        fields = "__all__"

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


class ARSerializer(BaseDynamicScreenSerializer):
    """
    Serializer for Annual Report.
    """

    class Meta:
        model = AnnualReport
        fields = "__all__"

    screen_fields_mapping = {
        "1": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "steps_taken_1",
            "steps_taken_description_1",
            "additional_information_2",
        ],
        "2": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "structure_3",
            "categorization_4",
            "additional_information_entity_5",
        ],
        "3": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "policies_in_place_6",
            "elements_implemented_6_1",
            "additional_info_policies_7",
        ],
        "4": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "risk_identified_8",
            "risk_aspects_8_1",
            "risk_aspects_description_8_1",
            "risk_activaties_9",
            "risk_activaties_description_9",
            "additional_info_entity_10",
        ],
        "5": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "measures_remediate_activaties_11",
            "remediation_measures_taken_11_1",
            "remediation_measures_taken_description_11_1",
            "remediation_measures_12",
        ],
        "6": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "measures_taken_loss_income_13",
            "additional_info_loss_income_14",
        ],
        "7": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "training_provided_15",
            "training_mandatory_15_1",
            "additional_info_training_16",
        ],
        "8": [
            "user_id",
            "organization_id",
            "corporate_id",
            "year",
            "policies_procedures_assess_17",
            "assessment_method_17_1",
            "assessment_method_description_17_1",
            "additional_info_assessment_18",
        ],
    }
