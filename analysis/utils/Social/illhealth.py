from common.utils.value_types import get_float
from analysis.models.Social.IllHealth import IllHealthReport
from datametric.models import RawResponse
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)


def ill_health_report_analysis(raw_response: RawResponse):
    if raw_response.path.slug == "gri-social-ohs-403-10a-ill_health_emp":
        table_name = "employees"
    elif raw_response.path.slug == "gri-social-ohs-403-10b-ill_health_workers":
        table_name = "non_employees"
    else:
        return
    IllHealthReport.objects.filter(
        raw_response=raw_response, table_name=table_name
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

        IllHealthReport.objects.update_or_create(
            raw_response=raw_response,
            table_name=table_name,
            month=raw_response.month,
            year=raw_response.year,
            organisation=organisation,
            corporate=corporate,
            location=raw_response.locale,
            client=raw_response.client,
            index=index,
            defaults={
                "employee_category": local_data["employeeCategory"],
                "fatalities_due_to_ill_health": get_float(local_data["fatalities"]),
                "recordable_ill_health_cases": get_float(local_data["recordable"]),
                "types_of_ill_health": local_data["highconsequence"],
            },
        )[0].save()
