from analysis.models.Water.WaterFromAllAreas import (
    WaterFromAllAreas,
    ThirdPartyWaterDischargeFromAllAreas,
)
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse
from common.enums.WaterEnums import WaterUnitChoices


def create_data_for_water_from_all_areas_analysis(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas"
    ):
        return
    WaterFromAllAreas.objects.filter(raw_response=raw_response).delete()
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
        water_from_all_areas_object, _ = WaterFromAllAreas.objects.update_or_create(
            raw_response=raw_response,
            month=raw_response.month,
            year=raw_response.year,
            organisation=organisation,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            index=index,
            defaults={
                "source": local_data["Source"],
                "water_type": local_data["Watertype"],
                "water_unit": local_data["Unit"],
                "business_operation": local_data["Businessoperations"],
                "total_water_withdrawal": get_float(local_data["withdrawal"]),
                "total_water_discharge": get_float(local_data["discharge"]),
            },
        )
        converted_withdrawal = water_from_all_areas_object.convert_to_megalitres(
            "total_water_withdrawal"
        )
        converted_discharge = water_from_all_areas_object.convert_to_megalitres(
            "total_water_discharge"
        )
        water_from_all_areas_object.total_water_withdrawal = converted_withdrawal
        water_from_all_areas_object.total_water_discharge = converted_discharge
        water_from_all_areas_object.water_unit = "Megalitre"
        water_from_all_areas_object.save()


def create_data_for_water_discharge_from_third_party(raw_response: RawResponse):
    if raw_response.path.slug != "gri-environment-water-303-4a-third_party":
        return
    ThirdPartyWaterDischargeFromAllAreas.objects.filter(
        raw_response=raw_response
    ).delete()
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
        water_discharge_from_third_party_object, _ = (
            ThirdPartyWaterDischargeFromAllAreas.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                client=raw_response.client,
                index=index,
                defaults={
                    "third_party_discharge": local_data["Discharge"],
                    "water_unit": local_data["Unit"],
                    "quantity": get_float(local_data["Volume"]),
                },
            )
        )
        water_discharge_from_third_party_object.quantity = (
            water_discharge_from_third_party_object.convert_to_megalitres("quantity")
        )
        water_discharge_from_third_party_object.water_unit = "Megalitre"
        water_discharge_from_third_party_object.save()
