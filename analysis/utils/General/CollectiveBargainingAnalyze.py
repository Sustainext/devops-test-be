from analysis.models.General.CollectiveBargaining import GeneralCollectiveBargaining
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_general_collective_bargaining(raw_response: RawResponse):

    if raw_response.path.slug != "gri-general-collective_bargaining-2-30-a-percentage":
        return
    cb = GeneralCollectiveBargaining.objects.filter(raw_response=raw_response)
    if cb:
        cb.delete()
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
        collective_bargaining_obj, _ = (
            GeneralCollectiveBargaining.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                client=raw_response.client,
                defaults={
                    "emp_covered_by_cb": get_float(response_item.get("Q1")),
                    "emp_in_org": get_float(response_item.get("Q2")),
                },
            )
        )
        collective_bargaining_obj.save()
