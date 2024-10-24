from analysis.models.Economic.CommunicationAndTraining import (
    EcoTotalBodyMembers,
    EcoTotalBodyMembersRegion,
)
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse
from logging import getLogger

logger = getLogger("error.log")
path_mapping = {
    0: "gri-economic-anti_corruption-comm_and_training-205-2a-governance_body_members",
    1: "gri-economic-anti_corruption-comm_and_training-205-2d-training",
    2: "gri-economic-anti_corruption-comm_and_training-205-2b-employees",
    3: "gri-economic-anti_corruption-comm_and_training-205-2c-business",
    4: "gri-economic-anti_corruption-comm_and_training-205-2e-policies",
}


def create_data_for_economic_total_body_members(raw_response: RawResponse):

    if raw_response.path.slug not in [path_mapping[0], path_mapping[1]]:
        return
    table_maping = {
        path_mapping[0]: "communicated anti-corruption policy - region",
        path_mapping[1]: "received training on anti-corruption - region",
    }
    oa = EcoTotalBodyMembers.objects.filter(raw_response=raw_response).delete()
    try:
        if raw_response.data[0]["Q1"]:
            pass
        else:
            logger.error(
                f"No data available for {raw_response.path.slug} with the raw response id {raw_response.id}"
            )
            return
    except Exception as e:
        logger.error(
            f"Error {e} occured while processing raw response id {raw_response.id}"
        )
        return {"errorr": e}
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
    for index, raw_item in enumerate(raw_response.data[0]["Q1"]):
        oa_obj, _ = EcoTotalBodyMembers.objects.update_or_create(
            raw_response=raw_response,
            month=raw_response.month,
            year=raw_response.year,
            organisation=organisation,
            corporate=corporate,
            location=location,
            index=index,
            client=raw_response.client,
            defaults={
                "location_name": raw_item.get("Location Name"),
                "table_name": table_maping[raw_response.path.slug],
                "specific_total": get_float(
                    raw_item.get(
                        "Total number of governance body members that the organization's anti-corruption policies and procedures have been communicated to"
                    )
                    if raw_response.path.slug == path_mapping[0]
                    else raw_item.get(
                        "Total number of governance body members that have received training on anti-corruption"
                    )
                ),
                "total": get_float(
                    raw_item.get(
                        "Total number of governance body members in that region."
                    )
                    if raw_response.path.slug == path_mapping[0]
                    else raw_item.get("Total number of governance body members")
                ),
            },
        )
        oa_obj.save()


def create_data_for_economic_total_body_members_region(raw_response: RawResponse):

    if raw_response.path.slug not in [
        path_mapping[4],
        path_mapping[3],
        path_mapping[2],
    ]:
        return
    table_maping = {
        path_mapping[2]: "communicated anti-corruption policy - emp category",
        path_mapping[3]: "communicated anti-corruption policy - business partner",
        path_mapping[4]: "received training on anti-corruption - region",
    }
    oa = EcoTotalBodyMembersRegion.objects.filter(raw_response=raw_response).delete()
    try:
        if raw_response.data[0]["Q1"]:
            pass
        else:

            logger.error(
                f"No data available for {raw_response.path.slug} with the raw response id {raw_response.id}"
            )
            return
    except Exception as e:
        logger.error(
            f"Error {e} occured while processing raw response id {raw_response.id}"
        )
        return {"errorr": e}
    for key, raw_item in raw_response.data[0]["Q1"].items():
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
        for index, item in enumerate(raw_item):
            oa_obj, _ = EcoTotalBodyMembersRegion.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                index=index,
                location_name=key,
                client=raw_response.client,
                defaults={
                    "table_name": table_maping[raw_response.path.slug],
                    "emp_category_or_business_partner": (
                        item.get("EmployeeCategory")
                        if raw_response.path.slug in [path_mapping[2], path_mapping[4]]
                        else item.get("Typeofbusinesspartner")
                    ),
                    "specific_total": get_float(item["Totalnumberemployees"]),
                    "total": get_float(item["Totalemployeeinthisregion"]),
                },
            )
            oa_obj.save()
