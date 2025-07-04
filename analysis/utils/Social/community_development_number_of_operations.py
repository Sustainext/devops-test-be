from analysis.models.Social.CommunityDevelopmentNumberOfOperation import (
    CommunityDevelopmentNumberOfOperation,
    OPERATION_CHOICES,
)
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from common.utils.value_types import get_float
from datametric.models import RawResponse


def create_data_for_community_development_number_of_operations(
    raw_response: RawResponse,
):
    """
    This function creates the data for the community development number of operations.
    """
    if (
        raw_response.path.slug
        != "gri-social-community_engagement-413-1a-number_of_operations"
    ):
        return
    CommunityDevelopmentNumberOfOperation.objects.filter(
        raw_response=raw_response
    ).delete()
    for index, entry in enumerate(raw_response.data):
        CommunityDevelopmentNumberOfOperation.objects.update_or_create(
            raw_response=raw_response,
            month=raw_response.month,
            year=raw_response.year,
            location=raw_response.locale,
            client=raw_response.client,
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
            index=index,
            defaults={
                "name_of_operation": OPERATION_CHOICES[index][0],
                "local_community_operations_count": get_float(entry["operations"]),
                "total_operations_count": get_float(entry["totaloperations"]),
            },
        )[0].save()
