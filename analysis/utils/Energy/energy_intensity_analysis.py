from analysis.models.Energy.Energy import EnergyIntensity
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from common.utils.value_types import get_integer, get_decimal
from datametric.models import RawResponse
from common.utils.energy_unit_converter import convert_to_gj


def create_data_for_energy_intensity_analysis(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-energy-302-3a-3b-3c-3d-energy_intensity"
    ):
        return
    EnergyIntensity.objects.filter(raw_response=raw_response).delete()
    for index, local_data in enumerate(raw_response.data):
        organization = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        EnergyIntensity.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organisation=organization,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            index=index,
            raw_response=raw_response,
            defaults={
                "energy_type": local_data["EnergyType"],
                "energy_quantity": get_decimal(local_data["EnergyQuantity"]),
                "energy_unit": local_data["Unit"],
                "org_metric": local_data["Organizationmetric"],
                "metric_quantity": get_decimal(local_data["Metricquantity"]),
                "metric_unit": local_data["Metricunit"],
            },
        )[0].save()
