from analysis.models.Waste.WasteDirectedToDisposal import WasteDirectedToDisposal
from common.utils.value_types import get_integer
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_waste_diverted_to_disposal_analysis(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-waste-306-5a-5b-5c-5d-5e-waste_diverted_to_disposal"
    ):
        return

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
        location = raw_response.locale
        waste_diverted_from_disposal_object, _ = (
            WasteDirectedToDisposal.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                index=index,
                defaults={
                    "waste_type": local_data["WasteType"],
                    "category": local_data["Wastecategory"],
                    "waste_disposed": get_integer(local_data["Wastedisposed"]),
                    "waste_unit": local_data["Unit"],
                    "method_of_disposal": local_data["Methodofdisposal"],
                    "site": local_data["Site"],
                },
            )
        )
        waste_diverted_from_disposal_object.convert_to_kilograms()
        waste_diverted_from_disposal_object.waste_unit = "Kgs"
        waste_diverted_from_disposal_object.save()
