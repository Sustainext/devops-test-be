from analysis.models.Social.GovernanceBodyDetails import GovernanceBodyDetails
from common.utils.value_types import get_integer
from datametric.models import RawResponse
from analysis.models.Social.GovernanceBodyDetails import GovernanceBodyDetails
from analysis.models.Social.Gender import Gender
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)


def create_data_for_governance_bodies_details(raw_response: RawResponse):
    """
    This function creates the data for the organisation governance bodies.
    """

    if raw_response.path.slug == "gri-social-salary_ratio-405-2a-number_of_individuals":
        table_name = "number_of_individuals_within_the_organizations_governance_bodies"
    elif (
        raw_response.path.slug == "gri-social-salary_ratio-405-2a-ratio_of_remuneration"
    ):
        table_name = "ratio_of_remuneration_of_women_to_men"
    else:
        return
    for index, entry in enumerate(raw_response.data):
        # Assuming 'male', 'female', and 'nonBinary' correspond to existing Gender entries
        genders = {
            "male": entry["male"],
            "female": entry["female"],
            "other": entry["nonBinary"],
        }

        for gender_name, count in genders.items():
            gender, created = Gender.objects.get_or_create(gender=gender_name)
            GovernanceBodyDetails.objects.update_or_create(
                month=raw_response.month,
                year=raw_response.year,
                location=raw_response.locale,
                table_name=table_name,
                organisation=(
                    raw_response.organization
                    if get_organisation(raw_response.locale) is None
                    else get_organisation(raw_response.locale)
                ),
                corporate=(
                    raw_response.corporate
                    if get_corporate(raw_response.locale) is None
                    else get_corporate(raw_response.locale)
                ),
                gender=gender,
                index=index,
                defaults={
                    "employee_category": entry["category"],
                    "gender_count": count,
                    "location_of_operation": entry["locationandoperation"],
                },  # Assuming AbstractAnalysisModel or AbstractModel has a location field
            )[0].save()
