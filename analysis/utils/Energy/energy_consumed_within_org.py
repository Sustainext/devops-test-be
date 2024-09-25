from analysis.models.Energy.Energy import (
    DirectPurchasedEnergy,
    ConsumedEnergy,
    SelfGeneratedEnergy,
    EnergySold,
)
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse
from common.utils.value_types import get_integer
from common.utils.energy_unit_converter import convert_to_gj


def create_data_for_direct_purchased_energy(raw_response: RawResponse):
    if raw_response.path.slug != "gri-environment-energy-302-1a-1b-direct_purchased":
        return
    
    for index, local_data in enumerate(raw_response.data):
        organisation = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        DirectPurchasedEnergy.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organization=organisation,
            corporate=corporate,
            location=location,
            index=index,
            raw_response=raw_response,
            defaults={
                "energy_type": local_data["EnergyType"],
                "source": local_data["Source"],
                "purpose": local_data["Purpose"],
                "renewability": local_data["Renewable"],
                "quantity": get_integer(local_data["Quantity"]),
                "unit": local_data["Unit"],
                "quantiy_gj": convert_to_gj(
                    quantity=get_integer(local_data["Quantity"]),
                    unit=local_data["Unit"],
                ),
            },
        )[0].save()


def create_data_for_consumed_energy(raw_response: RawResponse):
    if raw_response.path.slug != "gri-environment-energy-302-1c-1e-consumed_fuel":
        return

    for index, local_data in enumerate(raw_response.data):
        organisation = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        ConsumedEnergy.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organization=organisation,
            corporate=corporate,
            location=location,
            index=index,
            raw_response=raw_response,
            defaults={
                "energy_type": local_data["EnergyType"],
                "source": local_data["Source"],
                "purpose": local_data["Purpose"],
                "renewability": local_data["Renewable"],
                "quantity": get_integer(local_data["Quantity"]),
                "unit": local_data["Unit"],
                "quantiy_gj": convert_to_gj(
                    quantity=get_integer(local_data["Quantity"]),
                    unit=local_data["Unit"],
                ),
            },
        )[0].save()


def create_data_for_self_genereted(raw_response: RawResponse):
    if raw_response.path.slug != "gri-environment-energy-302-1-self_generated":
        return

    for index, local_data in enumerate(raw_response.data):
        organisation = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        SelfGeneratedEnergy.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organization=organisation,
            corporate=corporate,
            location=location,
            index=index,
            raw_response=raw_response,
            defaults={
                "energy_type": local_data["EnergyType"],
                "source": local_data["Source"],
                "renewability": local_data["Renewable"],
                "quantity": get_integer(local_data["Quantity"]),
                "unit": local_data["Unit"],
                "quantiy_gj": convert_to_gj(
                    quantity=get_integer(local_data["Quantity"]),
                    unit=local_data["Unit"],
                ),
            },
        )[0].save()


def create_data_for_energy_sold(raw_response: RawResponse):
    if raw_response.path.slug != "gri-environment-energy-302-1d-energy_sold":
        return

    for index, local_data in enumerate(raw_response.data):
        organisation = get_organisation(raw_response.locale)
        corporate = get_corporate(raw_response.locale)
        location = raw_response.locale
        EnergySold.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organization=organisation,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            index=index,
            raw_response=raw_response,
            defaults={
                "energy_type": local_data["EnergyType"],
                "source": local_data["Source"],
                "type_of_entity": local_data["Typeofentity"],
                "name_of_entity": local_data["Nameofentity"],
                "renewability": local_data["Renewable"],
                "quantity": get_integer(local_data["Quantity"]),
                "unit": local_data["Unit"],
                "quantiy_gj": convert_to_gj(
                    quantity=get_integer(local_data["Quantity"]),
                    unit=local_data["Unit"],
                ),
            },
        )[0].save()
