from datametric.models import RawResponse
from analysis.models.General.WorkForceEmp import GeneralTotalEmployees
from analysis.models.Social.Gender import Gender
from common.utils.value_types import get_float

EMPLOYMENT_TYPE_MAPPING = {
    "permanent_employee": "permanent employee",
    "temporary_employee": "temporary employee",
    "nonguaranteed_hours_employees": "non-guaranteed-employee",
    "full_time_employee": "full-time employee",
    "part_time_employee": "part-time employee",
}

AGE_GROUP_MAPPING = {
    "yearsold30": "less than 30 years old",
    "yearsold30to50": "30-50 years old",
    "yearsold50": "greater than 50 years old",
}


def get_employment_type(slug):
    return EMPLOYMENT_TYPE_MAPPING[slug.split("-")[-1]]


def get_age_group_and_value(data):
    return {
        AGE_GROUP_MAPPING[key]: get_float(value)
        for key, value in data.items()
        if key != "total"
    }


def get_gender(index):
    return Gender.objects.get(id=index + 1)


def create_data(raw_response: RawResponse):
    for index, local_data in enumerate(raw_response.data):
        age_group_and_value = get_age_group_and_value(local_data)
        for age_group, value in age_group_and_value.items():
            defaults = {"value": value}

            GeneralTotalEmployees.objects.update_or_create(
                month=raw_response.month,
                year=raw_response.year,
                location=raw_response.locale,
                organisation=raw_response.organization,
                corporate=raw_response.corporate,
                age_group=age_group,
                raw_response=raw_response,
                employment_type=get_employment_type(raw_response.path.slug),
                gender=get_gender(index),
                client=raw_response.client,
                index=index,
                defaults=defaults,
            )[0].save()


def total_number_employees_analysis(raw_response: RawResponse):
    path_slugs = {
        "gri-general-workforce_employees-2-7-a-b-permanent_employee": "general_per_emp",
        "gri-general-workforce_employees-2-7-a-b-temporary_employee": "general_temp_emp",
        "gri-general-workforce_employees-2-7-a-b-nonguaranteed_hours_employees": "general_ng_emp",
        "gri-general-workforce_employees-2-7-a-b-full_time_employee": "general_ft_emp",
        "gri-general-workforce_employees-2-7-a-b-part_time_employee": "general_pt_emp",
    }

    if raw_response.path.slug in path_slugs:
        GeneralTotalEmployees.objects.filter(raw_response=raw_response).delete()
        create_data(raw_response)
    else:
        return
