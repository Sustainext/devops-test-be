from analysis.models.Economic.MarketPresence import EcoStandardWages
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse
from analysis.models.Social.Gender import Gender
from logging import getLogger

logger = getLogger("error.log")


def gender_mapping(data):
    try:
        return {
            Gender.objects.get(id=1): data.get("Male"),
            Gender.objects.get(id=2): data.get("Female"),
            Gender.objects.get(id=3): data.get("Non-binary"),
        }
    except Gender.DoesNotExist as e:
        logger.error(f"Gender instance not found: {e}")
        return


def create_data_for_economic_standard_wages(raw_response: RawResponse):
    if raw_response.path.slug not in [
        "gri-economic-ratios_of_standard_entry_level_wage_by_gender_compared_to_local_minimum_wage-202-1a-s1",
    ]:
        return
    try:
        if raw_response.data[0]["Q2"] == "Yes":
            if raw_response.data[0]["Q4"]:
                pass
            else:
                logger.error(
                    f"{raw_response.id} was not processed as the required field Q4 dosen't have data"
                )
                return
        else:
            logger.error(
                f"{raw_response.id} was not processed as the required field Q2 was marked as No"
            )
            return
    except Exception as e:
        logger.error(
            f"Error {e} occured while processing raw response id {raw_response.id}"
        )
        return {"error": e}

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
    currency = raw_response.data[0]["Q3"] if raw_response.data[0]["Q3"] else None
    mp = EcoStandardWages.objects.filter(raw_response=raw_response).delete()

    try:
        min_wages_for_loc = RawResponse.objects.filter(
            organization=organisation,
            corporate=corporate,
            client=raw_response.client,
            locale=location,
            year=raw_response.year,
            month=raw_response.month,
            path__slug="gri-economic-ratios_of_standard_entry-202-1c-location",
        ).first()
        if min_wages_for_loc:
            min_wage = min_wages_for_loc.data[0]["Currency"].split(" ")[0]
            min_wage_currency = min_wages_for_loc.data[0]["Currency"].split(" ")[1]
        else:
            min_wage = None
            min_wage_currency = None
    except Exception as e:
        logger.error(
            f"Error {e} occured while processing raw response id {raw_response.id}"
        )
    for index, raw_item in enumerate(raw_response.data[0]["Q4"]):

        gm_item = gender_mapping(raw_item)
        for key, value in gm_item.items():
            mp_obj, create = EcoStandardWages.objects.update_or_create(
                raw_response=raw_response,
                month=raw_response.month,
                year=raw_response.year,
                organisation=organisation,
                corporate=corporate,
                location=location,
                index=index,
                gender=key,
                client=raw_response.client,
                location_name=raw_item.get("Location"),
                defaults={
                    "currency": currency,
                    "value": get_float(value),
                    "minimum_wage": min_wage,
                    "minimum_wage_currency": min_wage_currency,
                },
            )
            mp_obj.save()
            logger.error(f"obj is created : {create}")
