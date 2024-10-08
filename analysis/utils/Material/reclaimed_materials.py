from analysis.models.Material.ReclaimedMaterials import ReclaimedMaterials
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse


def create_data_for_reclaimed_materials(raw_response: RawResponse):
    if (
        raw_response.path.slug
        != "gri-environment-materials-301-3a-3b-reclaimed_products"
    ):
        return
    ReclaimedMaterials.objects.filter(raw_response=raw_response).delete()
    for index, form_data in enumerate(raw_response.data):
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
        # Create or update the ReclaimedMaterials object
        reclaimed_materials_object, _ = ReclaimedMaterials.objects.update_or_create(
            raw_response=raw_response,
            month=raw_response.month,
            year=raw_response.year,
            organisation=organisation,
            corporate=corporate,
            location=location,
            client=raw_response.client,
            index=index,
            defaults={
                "type_of_product_sold": form_data["Typesofproducts"],
                "product_classification": form_data["Productclassification"],
                "product_code": form_data["Productcode"],
                "product_name": form_data["Productname"],
                "amount_of_product_sold": get_float(form_data["Amountofproducts"]),
                "product_sold_unit": form_data["Unit"],
                "recycled_material_used": form_data["Recycledmaterialsused"],
                "type_of_recycled_material_used": form_data["Typesofrecycledmaterials"],
                "amount_of_recycled_material_used": get_float(
                    form_data["Amountsproduct"]
                ),
                "recycled_material_used_unit": form_data["Unit2"],
                "data_collection_method": form_data["Datacollectionmethod"],
            },
        )
        reclaimed_materials_object.save()
