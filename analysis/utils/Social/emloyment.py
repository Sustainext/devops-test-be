from datametric.models import RawResponse
from analysis.models.Social.EmployeeTurnOver import EmploymentTurnover
from analysis.models.Social.EmploymentHires import EmploymentHires
from analysis.models.Social.Gender import Gender
from analysis.models.Social.ParentalLeave import ParentalLeave, EMPLOYEE_CATEGORIES
from common.utils.value_types import get_integer

EMPLOYMENT_TYPE_MAPPING = {
    "permanent_emp": "permanent employee",
    "temp_emp": "temporary employee",
    "nonguaranteed": "non-guaranteed-employee",
    "fulltime": "full-time employee",
    "parttime": "part-time employee",
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
        AGE_GROUP_MAPPING[key]: get_integer(value)
        for key, value in data.items()
        if key not in ["total", "beginning", "end"]
    }


def get_gender(index):
    return Gender.objects.get(id=index + 1)


def create_data(raw_response: RawResponse, table_name, model):
    for index, local_data in enumerate(raw_response.data):
        age_group_and_value = get_age_group_and_value(local_data)
        for age_group, value in age_group_and_value.items():
            defaults = {"value": value}
            if model == EmploymentTurnover:
                defaults.update(
                    {
                        "employee_turnover_beginning": get_integer(
                            local_data.get("beginning", 0)
                        ),
                        "employee_turnover_ending": get_integer(
                            local_data.get("end", 0)
                        ),
                    }
                )

            model.objects.update_or_create(
                month=raw_response.month,
                year=raw_response.year,
                location=raw_response.locale,
                organisation=raw_response.locale.corporateentity.organization,
                corporate=raw_response.locale.corporateentity,
                age_group=age_group,
                raw_response=raw_response,
                employment_type=get_employment_type(raw_response.path.slug),
                gender=get_gender(index),
                employmee_table_name=table_name,
                client=raw_response.client,
                index=index,
                defaults=defaults,
            )[0].save()


def employment_analysis(raw_response: RawResponse):
    path_slugs = {
        "new employee hire": (
            "gri-social-employee_hires-401-1a-new_emp_hire",
            EmploymentHires,
        ),
        "employee turnover": (
            "gri-social-employee_hires-401-1a-emp_turnover",
            EmploymentTurnover,
        ),
    }

    for table_name, (slug_prefix, model) in path_slugs.items():
        if raw_response.path.slug.startswith(slug_prefix):
            create_data(raw_response, table_name, model)
            break


def parental_leave_analysis(raw_response: RawResponse):
    if (
        "gri-social-parental_leave-401-3a-3b-3c-3d-parental_leave"
        == raw_response.path.slug
    ):

        for index, category_data in enumerate(raw_response.data):
            category_data.pop("total")
            for gender, value in category_data.items():
                ParentalLeave.objects.update_or_create(
                    raw_response=raw_response,
                    month=raw_response.month,
                    year=raw_response.year,
                    location=raw_response.locale,
                    client=raw_response.client,
                    organisation=raw_response.locale.corporateentity.organization,
                    corporate=raw_response.locale.corporateentity,
                    gender=Gender.objects.get(gender=gender),
                    employee_category=EMPLOYEE_CATEGORIES[index][0],
                    defaults={"value": get_integer(value)},
                )[0].save()
