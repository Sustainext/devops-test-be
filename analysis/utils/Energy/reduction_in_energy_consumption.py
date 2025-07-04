from analysis.models.Energy.Energy import ReductionEnergyConsumption
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from common.utils.value_types import get_float
from datametric.models import RawResponse
from common.utils.energy_unit_converter import convert_to_gj


def create_data_for_reduction_in_energy_consumption(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-energy-302-4a-4b-reduction_of_energy_consumption"
    ):
        return
    ReductionEnergyConsumption.objects.filter(raw_response=raw_response).delete()
    for index, local_data in enumerate(raw_response.data):
        organisation = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        ReductionEnergyConsumption.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organization=organisation,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            index=index,
            raw_response=raw_response,
            defaults={
                "type_of_intervention": local_data["Typeofintervention"],
                "energy_type_reduced": local_data["Energytypereduced"],
                "base_year": get_float(local_data["Baseyear"]),
                "energy_reduction": local_data["Energyreductionis"],
                "methodology_used": local_data["Methodologyused"],
                "quantity": get_float(local_data["Quantitysavedduetointervention"]),
                "unit": local_data["Unit"],
                "quantiy_gj": convert_to_gj(
                    quantity=get_float(local_data["Quantitysavedduetointervention"]),
                    unit=local_data["Unit"],
                ),
            },
        )[0].save()
