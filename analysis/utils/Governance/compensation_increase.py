from analysis.models.Governance.CompensationIncrease import CompensationIncrease
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def fill_data_inside_compensation_increase(raw_response: RawResponse):
    if raw_response.path.slug != "gri-governance-compensation_ratio-2-21-b-percentage":
        return
    CompensationIncrease.objects.filter(raw_response=raw_response).delete()
    for index, response_item in enumerate(raw_response.data):
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
        compensation_increase_object, _ = CompensationIncrease.objects.update_or_create(
            raw_response=raw_response,
            month=raw_response.month,
            year=raw_response.year,
            organisation=organisation,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            defaults={
                "highest_paid_individual_percentage_increase": get_float(
                    response_item.get("Q1")
                ),
                "median_employee_percentage_increase": get_float(
                    response_item.get("Q2")
                ),
            },
        )
        compensation_increase_object.save()
