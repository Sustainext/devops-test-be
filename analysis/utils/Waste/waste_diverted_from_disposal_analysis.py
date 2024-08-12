from analysis.models.Waste.WasteDivertedFromDisposal import WasteDivertedFromDisposal
from common.utils.value_types import get_integer
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_waste_diverted_from_disposal_analysis(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-waste-306-4b-4c-4d-waste_diverted_from_disposal"
    ):
        return

    for index, local_data in enumerate(raw_response.data):
        organisation = (
            raw_response.organization
            if get_organisation(raw_response) is None
            else get_organisation(raw_response)
        )
        corporate = (
            raw_response.corporate
            if get_corporate(raw_response) is None
            else get_corporate(raw_response)
        )
        location = raw_response.locale
        waste_diverted_from_disposal, _ = (
            WasteDivertedFromDisposal.objects.update_or_create(
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                index=index,
                defaults={
                    "waste_type": local_data["WasteType"],
                    "category": local_data["Wastecategory"],
                    "waste_diverted": get_integer(local_data["Wastediverted"]),
                    "waste_unit": local_data["Unit"],
                    "site": local_data["Site"],
                },
            )
        )
        waste_diverted_from_disposal.convert_to_kilograms()
        waste_diverted_from_disposal.waste_unit = "Kgs"
        waste_diverted_from_disposal.save()
