from analysis.models.Water.WaterFromStressAreas import (
    WaterFromStressAreas,
    WaterDischargeFromStressAreas,
)
from common.utils.value_types import get_integer
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_water_from_stress_areas(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress"
    ):
        return

    for response_item in raw_response.data:
        form_data_list = response_item.get("formData", [])

        for index, form_data in enumerate(form_data_list):
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
            water_from_stress_areas_object, _ = (
                WaterFromStressAreas.objects.update_or_create(
                    raw_response=raw_response,
                    month=raw_response.month,
                    year=raw_response.year,
                    organisation=organisation,
                    corporate=corporate,
                    location=location,
                    client=raw_response.client,
                    index=index,
                    defaults={
                        "source": form_data["Source"],
                        "water_type": form_data["Watertype"],
                        "water_unit": form_data["Unit"],
                        "business_operation": form_data["Businessoperations"],
                        "name_of_water_stress_area": form_data["waterstress"],
                        "pin_code": form_data["Pincode"],
                        "total_water_withdrawal": get_integer(
                            form_data["Waterwithdrawal"]
                        ),
                        "total_water_discharge": get_integer(
                            form_data["Waterdischarge"]
                        ),
                    },
                )
            )
            converted_withdrawal = water_from_stress_areas_object.convert_to_megalitres(
                "total_water_withdrawal"
            )
            converted_discharge = water_from_stress_areas_object.convert_to_megalitres(
                "total_water_discharge"
            )

            water_from_stress_areas_object.total_water_withdrawal = converted_withdrawal
            water_from_stress_areas_object.total_water_discharge = converted_discharge

            water_from_stress_areas_object.water_unit = "Megalitre"
            water_from_stress_areas_object.save()


def create_data_for_water_discharge_from_stress_areas(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-water-303-3b-water_withdrawal_areas_water_stress"
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
        water_withdraw_from_stress_areas_object, _ = (
            WaterDischargeFromStressAreas.objects.update_or_create(
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
                    "withdraw_from_third_party": local_data["Discharge"],
                    "unit": local_data["Unit"],
                    "quantity": get_integer(local_data["Quantity"]),
                },
            )
        )
        water_withdraw_from_stress_areas_object.quantity = (
            water_withdraw_from_stress_areas_object.convert_to_megalitres("quantity")
        )
        water_withdraw_from_stress_areas_object.unit = "Megalitre"
        water_withdraw_from_stress_areas_object.save()
