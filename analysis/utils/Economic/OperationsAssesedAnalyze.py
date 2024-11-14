from analysis.models.Economic.OperationsAssesed import EcoOperationsAssesed
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_economic_operations_assesed(raw_response: RawResponse):

    if (
        raw_response.path.slug
        != "gri-economic-operations_assessed_for_risks_related_to_corruption-205-1a-total"
    ):
        return
    oa = EcoOperationsAssesed.objects.filter(raw_response=raw_response)
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
    location = raw_response.locale
    oa_obj, _ = EcoOperationsAssesed.objects.update_or_create(
        raw_response=raw_response,
        month=raw_response.month,
        year=raw_response.year,
        organisation=organisation,
        corporate=corporate,
        location=location,
        client=raw_response.client,
        defaults={
            "operations_assessed": get_float(raw_response.data[0].get("Q1")),
            "operations": get_float(raw_response.data[0].get("Q2")),
        },
    )
    oa_obj.save()
