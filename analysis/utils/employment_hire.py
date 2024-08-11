from datametric.models import RawResponse
from analysis.models.EmploymentHires import EmploymentHires
from analysis.models.Gender import Gender

EMPLOYMENT_TYPE_MAPPING = {
    "permanent_emp": "permanent employee",
    "temp_emp": "temporary employee",
    "nongauranteed": "non-guaranteed-employee",
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


def get_integer(value):
    try:
        return int(value)
    except ValueError:
        return 0


def get_age_group_and_value(data):
    return {
        AGE_GROUP_MAPPING["yearsold30"]: get_integer(data["yearsold30"]),
        AGE_GROUP_MAPPING["yearsold30to50"]: get_integer(data["yearsold30to50"]),
        AGE_GROUP_MAPPING["yearsold50"]: get_integer(data["yearsold50"]),
    }


def get_gender(index):
    return Gender.objects.get(id=index + 1)


def create_data(raw_response: RawResponse, table_name):
    for local_data in raw_response.data:
        age_group_and_value = get_age_group_and_value(local_data)
        for index, (age_group, value) in enumerate(age_group_and_value.items()):
            employment_object, _ = EmploymentHires.objects.update_or_create(
                month=raw_response.month,
                year=raw_response.year,
                location=raw_response.locale,
                organisation=raw_response.locale.corporateentity.organization,
                corporate=raw_response.locale.corporateentity,
                age_group=age_group,
                employment_type=get_employment_type(raw_response.path.slug),
                gender=get_gender(index),
                employmee_table_name=table_name,
                defaults={"value": value},
            )
            employment_object.save()


def employment_hire_analysis(raw_response: RawResponse):
    path_slugs = {
        "new employee hire": "gri-social-employee_hires-401-1a-new_emp_hire",
        # "employee turnover": "gri-social-employee_hires-401-1a-emp_turnover",
    }

    for table_name, slug_prefix in path_slugs.items():
        if raw_response.path.slug.startswith(slug_prefix):
            create_data(raw_response, table_name)
            break
