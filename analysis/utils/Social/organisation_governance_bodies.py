from analysis.models.Social.OrganisationGovernanceBodies import (
    OrganisationGovernanceBodies,
)
from common.utils.value_types import get_float
from common.enums.Social import AGE_GROUP_CHOICES
from analysis.models.Social.Gender import Gender
from datametric.models import RawResponse
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)

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
    if not (
        raw_response.path.slug
        == "gri-social-diversity_of_board-405-1a-number_of_individuals"
        or raw_response.path.slug
        == "gri-social-diversity_of_board-405-1b-number_of_employee"
    ):
        return

    if (
        raw_response.path.slug
        == "gri-social-diversity_of_board-405-1a-number_of_individuals"
    ):
        table_name = "Number of individuals within the organizations governance bodies"
    elif (
        raw_response.path.slug
        == "gri-social-diversity_of_board-405-1b-number_of_employee"
    ):
        table_name = "Number of employees per employee category"
    OrganisationGovernanceBodies.objects.filter(
        raw_response=raw_response, table_name=table_name
    ).delete()
    for index, local_data in enumerate(raw_response.data):
        organisation = (
            raw_response.organization
            if get_organisation(raw_response.locale) is None
            else get_organisation(raw_response.locale)
        )
        corporate = (
            raw_response.corporate
            if get_corporate(raw_response.locale) is None
            else get_corporate(raw_response.locale)
        )
        age_group_and_value = get_age_group_and_value(local_data)
        gender_group_and_value = get_gender(local_data)

        for age_group, age_group_value in age_group_and_value.items():
            for gender, gender_value in gender_group_and_value.items():
                defaults = {
                    "age_group_value": age_group_value,
                    "gender_value": gender_value,
                    "minority_group_count": get_float(
                        local_data.get("minorityGroup", 0)
                    ),
                    "vulnerable_communities_count": get_float(
                        local_data.get("vulnerableCommunities", 0)
                    ),
                    "employee_category": local_data["category"],
                }
                OrganisationGovernanceBodies.objects.update_or_create(
                    raw_response=raw_response,
                    month=raw_response.month,
                    year=raw_response.year,
                    location=raw_response.locale,
                    organisation=organisation,
                    corporate=corporate,
                    client=raw_response.client,
                    index=index,
                    age_group=age_group,
                    table_name=table_name,
                    gender=Gender.objects.get_or_create(gender=gender)[0],
                    defaults=defaults,
                )[0].save()
