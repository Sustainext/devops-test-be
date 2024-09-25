from analysis.models.Water.ChangeInWaterStorage import ChangeInWaterStorage
from common.utils.value_types import get_integer
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse



def create_data_for_change_in_water_storage(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-water-303-5c-change_in_water_storage"
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
            change_in_water_storage_object, _ = (
                ChangeInWaterStorage.objects.update_or_create(
                    raw_response=raw_response,
                    month=raw_response.month,
                    year=raw_response.year,
                    organisation=organisation,
                    corporate=corporate,
                    location=location,
                    client=raw_response.client,
                    index=index,
                    defaults={
                        "unit": form_data["Unit"],
                        "total_water_storage_at_end": get_integer(
                            form_data["Reporting1"]
                        ),
                        "total_water_storage_at_beginning": get_integer(
                            form_data["Reporting2"]
                        ),
                        "change_in_water_storage": get_integer(
                            form_data["Reporting3"]
                        ),
                    },
                )
            )
            change_in_water_storage_object.total_water_storage_at_end = change_in_water_storage_object.convert_to_megalitres("total_water_storage_at_end")
            change_in_water_storage_object.total_water_storage_at_beginning = change_in_water_storage_object.convert_to_megalitres("total_water_storage_at_beginning")
            change_in_water_storage_object.change_in_water_storage = change_in_water_storage_object.convert_to_megalitres("change_in_water_storage")

            change_in_water_storage_object.unit = "Megalitre"
            change_in_water_storage_object.save()