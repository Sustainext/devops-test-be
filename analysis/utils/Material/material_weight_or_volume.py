from analysis.models.Material.MaterialUsedByWeightOrVolume import (
    NonRenewableMaterials,
    RenewableMaterials,
)
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_non_renewable_materials(raw_response: RawResponse):
    if raw_response.path.slug not in [
        "gri-environment-materials-301-1a-non_renewable_materials",
        "gri-environment-materials-301-1a-renewable_materials",
    ]:
        return

    if (
        raw_response.path.slug
        == "gri-environment-materials-301-1a-non_renewable_materials"
    ):
        NonRenewableMaterials.objects.filter(raw_response=raw_response).delete()

    if raw_response.path.slug == "gri-environment-materials-301-1a-renewable_materials":
        RenewableMaterials.objects.filter(raw_response=raw_response).delete()
    for index, response_item in enumerate(raw_response.data):

        # Use the organisation and corporate data from the locale if available
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

        # Create or update the NonRenewableMaterials object
        if (
            raw_response.path.slug
            == "gri-environment-materials-301-1a-non_renewable_materials"
        ):
            non_renewable_materials_object, _ = (
                NonRenewableMaterials.objects.update_or_create(
                    raw_response=raw_response,
                    month=raw_response.month,
                    year=raw_response.year,
                    organisation=organisation,
                    corporate=corporate,
                    location=location,
                    client=raw_response.client,
                    index=index,
                    defaults={
                        "type_of_material": response_item["Typeofmaterial"],
                        "material_used": response_item["Materialsused"],
                        "source": response_item["Source"],
                        "quantity": get_float(response_item["Totalweight"]),
                        "unit": response_item["Unit"],
                        "data_source": response_item["Datasource"],
                    },
                )
            )
            base_unit = non_renewable_materials_object.get_base_unit(
                non_renewable_materials_object.unit
            )
            non_renewable_materials_object.quantity = (
                non_renewable_materials_object.convert(
                    value=non_renewable_materials_object.quantity,
                    from_unit=non_renewable_materials_object.unit,
                    to_unit=base_unit,
                )
            )
            non_renewable_materials_object.unit = base_unit
            non_renewable_materials_object.save()
        else:
            renewable_materials_object, _ = RenewableMaterials.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                client=raw_response.client,
                index=index,
                defaults={
                    "type_of_material": response_item["Typeofmaterial"],
                    "material_used": response_item["Materialsused"],
                    "source": response_item["Source"],
                    "quantity": get_float(response_item["Totalweight"]),
                    "unit": response_item["Unit"],
                    "data_source": response_item["Datasource"],
                },
            )
            base_unit = renewable_materials_object.get_base_unit(
                renewable_materials_object.unit
            )
            renewable_materials_object.quantity = renewable_materials_object.convert(
                value=renewable_materials_object.quantity,
                from_unit=renewable_materials_object.unit,
                to_unit=base_unit,
            )
            renewable_materials_object.unit = base_unit
            renewable_materials_object.save()
