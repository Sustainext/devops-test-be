from analysis.models.Material.RecycledInputMaterials import RecycledInputMaterials
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_recycled_input_materials(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-materials-301-2a-recycled_input_materials"
    ):
        return
    RecycledInputMaterials.objects.filter(raw_response=raw_response).delete()

    for index, form_data in enumerate(raw_response.data):
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
        recycled_input_materials_object, _ = (
            RecycledInputMaterials.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                client=raw_response.client,
                index=index,
                defaults={
                    "recycled_material": form_data["Recycledmaterialsused"],
                    "type_of_recycled_material": form_data[
                        "Typeofrecycledmaterialused"
                    ],
                    "total_weight_or_volume": get_float(form_data["Totalweight"]),
                    "amount_of_material_recycled": get_float(
                        form_data["Amountofmaterialrecycled"]
                    ),
                    "amount_of_recycled_input_material_used": get_float(
                        form_data["Amountofrecycledinputmaterialused"]
                    ),
                    "unit_material_recycled": form_data["Unit"],
                    "unit_input_material_used": form_data["Unit2"],
                },
            )
        )
        recycled_input_materials_object.save()
