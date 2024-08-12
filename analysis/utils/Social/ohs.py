from analysis.models.Social.OHSEmployeeWorkerData import EmployeeWorkerData, CATEGORY_CHOICES
from analysis.models.Social.InjuryReport import InjuryReport, INJURIES_FOR_WHOM_CHOICES
from common.utils.value_types import get_integer
from datametric.models import RawResponse


def ohs_employee_worker_data(raw_response: RawResponse):
    if "gri-social-ohs-403-8a-number_of_employees" == raw_response.path.slug:
        for index, employee_type_data in enumerate(raw_response.data):
            category = CATEGORY_CHOICES[index][0]
            EmployeeWorkerData.objects.update_or_create(
                month=raw_response.month,
                year=raw_response.year,
                organisation=raw_response.locale.corporateentity.organization,
                corporate=raw_response.locale.corporateentity,
                location=raw_response.locale,
                category=category,
                defaults={
                    "number_of_employees": get_integer(
                        employee_type_data["coveredbythesystem"]
                    ),
                    "number_of_workers_not_employees": get_integer(
                        employee_type_data["externalparty"]
                    ),
                    "total_number_of_employees": get_integer(
                        employee_type_data["internallyaudited"]
                    ),
                },
            )[0].save()


def ohs_the_number_of_injuries(raw_response: RawResponse):
    if "gri-social-ohs-403-9a-number_of_injuries_emp" == raw_response.path.slug:
        table_name = INJURIES_FOR_WHOM_CHOICES[0][0]
    elif "gri-social-ohs-403-9b-number_of_injuries_workers" == raw_response.path.slug:
        table_name = INJURIES_FOR_WHOM_CHOICES[1][0]
    else:
        return
    for local_data in raw_response.data:
        InjuryReport.objects.update_or_create(
            month=raw_response.month,
            year=raw_response.year,
            organisation=raw_response.locale.corporateentity.organization,
            corporate=raw_response.locale.corporateentity,
            location=raw_response.locale,
            table_name=table_name,
            defaults={
                "employee_category": local_data["employeeCategory"],
                "fatalities": get_integer(local_data["fatalities"]),
                "high_consequence_injuries": get_integer(local_data["highconsequence"]),
                "recordable_injuries": get_integer(local_data["recordable"]),
                "injury_types": local_data["maintypes"],
                "hours_worked": get_integer(local_data["numberofhoursworked"]),
            },
        )[0].save()
