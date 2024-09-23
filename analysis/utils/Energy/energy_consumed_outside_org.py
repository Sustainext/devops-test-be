from analysis.models.Energy.Energy import EnergyConsumedOutsideOrg
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from common.utils.value_types import get_integer, get_decimal
from datametric.models import RawResponse
from common.utils.energy_unit_converter import convert_to_gj


def create_data_for_energy_consumed_outsid_org_analysis(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-energy-302-2a-energy_consumption_outside_organization"
    ):
        return

    for index, local_data in enumerate(raw_response.data):
        organization = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        EnergyConsumedOutsideOrg.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organization=organization,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            index=index,
            raw_response=raw_response,
            defaults={
                "energy_type": local_data["EnergyType"],
                "purpose": local_data["Purpose"],
                "quantity": get_integer(local_data["Quantity"]),
                "unit": local_data["Unit"],
                "quantiy_gj": convert_to_gj(
                    quantity=get_integer(local_data["Quantity"]),
                    unit=local_data["Unit"],
                ),
            },
        )[0].save()

