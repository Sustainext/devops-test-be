from analysis.models.Waste.WasteDivertedFromDisposal import WasteDivertedFromDisposal
from common.utils.value_types import get_float
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
    WasteDivertedFromDisposal.objects.filter(raw_response=raw_response).delete()
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
        waste_diverted_from_disposal, _ = (
            WasteDivertedFromDisposal.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                client=raw_response.client,
                index=index,
                defaults={
                    "waste_type": local_data["WasteType"],
                    "category": local_data["Wastecategory"],
                    "recovery_option": local_data["RecoveryOperations"],
                    "waste_diverted": get_float(local_data["Wastediverted"]),
                    "waste_unit": local_data["Unit"],
                    "site": local_data["Site"],
                },
            )
        )
        waste_diverted_from_disposal.waste_diverted = (
            waste_diverted_from_disposal.convert_to_kilograms()
        )
        waste_diverted_from_disposal.waste_unit = "Kgs"
        waste_diverted_from_disposal.save()
