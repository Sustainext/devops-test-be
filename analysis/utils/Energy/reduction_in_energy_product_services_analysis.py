from analysis.models.Energy.Energy import ReductionEnergyInProductServices
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from common.utils.energy_unit_converter import convert_to_gj
from common.utils.value_types import get_integer
from datametric.models import RawResponse


def create_data_for_reduction_in_energy_product_services(raw_response: RawResponse):
    if (
        "gri-environment-energy-302-5a-5b-reduction_in_energy_in_products_and_servies"
        != raw_response.path.slug
    ):
        return

    for index, local_data in enumerate(raw_response.data):
        organisation = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        ReductionEnergyInProductServices.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organization=organisation,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            index=index,
            raw_response=raw_response,
            defaults={
                "product": local_data["ProductServices"],
                "base_year": get_integer(local_data["Baseyear"]),
                "quantity": get_integer(local_data["Quantity"]),
                "quantiy_gj": convert_to_gj(
                    quantity=get_integer(local_data["Quantity"]),
                    unit=local_data["Unit"],
                ),
                "unit": "GJ",
            },
        )[0].save()
