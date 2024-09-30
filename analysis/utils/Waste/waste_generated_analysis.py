from common.utils.value_types import get_integer
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from analysis.models.Waste.WasteGenerated import WasteGenerated
from datametric.models import RawResponse


def create_data_for_waste_generated_analysis(raw_response: RawResponse):
    if raw_response.path.slug != "gri-environment-waste-306-3a-3b-waste_generated":
        return
    WasteGenerated.objects.filter(raw_response=raw_response).delete()
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
        waste_generated_object, _ = WasteGenerated.objects.update_or_create(
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
                "waste_generated": get_integer(local_data["Wastegenerated"]),
                "waste_unit": local_data["Unit"],
            },
        )
        standard_weight = waste_generated_object.convert_to_kilograms()
        waste_generated_object.waste_generated = standard_weight
        waste_generated_object.waste_unit = "Kgs"
        waste_generated_object.save()
