from common.utils.value_types import get_integer
from analysis.models.IllHealth import IllHealthReport
from datametric.models import RawResponse


def ill_health_report_analysis(raw_response: RawResponse):
    if raw_response.path.slug == "gri-social-ohs-403-10a-ill_health_emp":
        table_name = "employees"
    elif raw_response.path.slug == "gri-social-ohs-403-10b-ill_health_workers":
        table_name = "non_employees"
    else:
        return
    for local_data in raw_response.data:
        IllHealthReport.objects.update_or_create(
            table_name=table_name,
            month=raw_response.month,
            year=raw_response.year,
            organization=raw_response.locale.corporateentity.organization,
            corporate=raw_response.locale.corporateentity,
            location=raw_response.locale.location,
            defaults={
                "employee_category": local_data["employeeCategory"],
                "fatalities_due_to_ill_health": get_integer(local_data["fatalities"]),
                "recordable_ill_health_cases": get_integer(local_data["recordable"]),
                "types_of_ill_health": local_data["highconsequence"],
            },
        )[0].save()
