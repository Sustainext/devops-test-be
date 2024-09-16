from analysis.models.Social.OrganisationGovernanceBodies import (
    OrganisationGovernanceBodies,
)
from common.utils.value_types import get_integer
from common.enums.Social import AGE_GROUP_CHOICES
from analysis.models.Social.Gender import Gender
from datametric.models import RawResponse

AGE_GROUP_MAPPING = {
    "lessThan30": "less than 30 years old",
    "between30and50": "30-50 years old",
    "moreThan50": "greater than 50 years old",
}


def get_age_group_and_value(data):
    return {
        AGE_GROUP_MAPPING["lessThan30"]: data["lessThan30"],
        AGE_GROUP_MAPPING["between30and50"]: data["between30and50"],
        AGE_GROUP_MAPPING["moreThan50"]: data["moreThan50"],
    }


def get_gender(local_data):
    return {
        "male": local_data["male"],
        "female": local_data["female"],
        "other": local_data["nonBinary"],
    }


def create_data_for_organisation_governance_bodies(raw_response: RawResponse):
    if (
        raw_response.path.slug
        == "gri-social-diversity_of_board-405-1a-number_of_individuals"
    ):
        table_name = "Number of individuals within the organizations governance bodies"
    elif (
        raw_response.path.slug
        == "gri-social-diversity_of_board-405-1b-number_of_employee"
    ):
        table_name = "Number of employee per employee category"
    for index, local_data in enumerate(raw_response.data):
        age_group_and_value = get_age_group_and_value(local_data)
        gender_group_and_value = get_gender(local_data)
        for age_group, age_group_value in age_group_and_value.items():
            for gender, gender_value in gender_group_and_value.items():
                defaults = {
                    "age_group_value": age_group_value,
                    "gender_value": gender_value,
                    "minority_group_count": get_integer(
                        local_data.get("minorityGroup", 0)
                    ),
                    "vulnerable_communities_count": get_integer(
                        local_data.get("vulnerableCommunities", 0)
                    ),
                    "employee_category": local_data["category"],
                }
                OrganisationGovernanceBodies.objects.update_or_create(
                    raw_response=raw_response,
                    month=raw_response.month,
                    year=raw_response.year,
                    location=raw_response.locale,
                    organisation=raw_response.organization,
                    corporate=raw_response.corporate,
                    defaults=defaults,
                    index=index,
                    age_group=age_group,
                    table_name=table_name,
                    gender=Gender.objects.get(gender=gender),
                )[0].save()
