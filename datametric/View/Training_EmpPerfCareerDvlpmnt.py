from datametric.models import DataPoint, RawResponse
from logging import getLogger

logger = getLogger("error.log")
"""
Employment > Diversity of Employee : Is where we have to get the categories from
Training and Development > Employee Performance and career development: is where we show the cattegories
"""


def get_categories_serilalized_raw_response(resp, dps):
    """
    This function takes in a serialized raw response and returns a list of categories
    """
    categories_of_rawresp = []
    categories = {}
    for item in resp[0]["employeeCategories"]:
        if item["category"] in dps:
            categories.update({item["category"]: item})
            categories_of_rawresp.append(item)
    return categories, categories_of_rawresp


def extract_from_diversity_employee(serialized_raw_response, **kwargs):
    # TODO: Handle the case wher there is already data in the Training> Employee performance and career development. And the categories are updated under Employment > Diversity of Employee
    try:
        dps = (
            DataPoint.objects.filter(**kwargs, metric_name="category")
            .values_list("value", flat=True)
            .order_by("id")
        )

        resp = (
            serialized_raw_response.data[0]["data"]
            if serialized_raw_response.data
            else {}
        )
        categories, categories_of_rawresp = {}, []
        if resp:
            categories, categories_of_rawresp = get_categories_serilalized_raw_response(
                resp, dps
            )

        response = {
            "employeeCategories": [],
            "genders": [
                {"gender": "Male", "performance": "", "careerDevelopment": ""},
                {"gender": "Female", "performance": "", "careerDevelopment": ""},
                {"gender": "Non-Binary", "performance": "", "careerDevelopment": ""},
            ],
            "totalPerformance": 0,
            "totalCareerDevelopment": 0,
        }
        # Check if datapoints are there and if any new categories are added to employement
        if dps and serialized_raw_response.data:
            for dp in dps:
                if dp not in categories:
                    # print(resp)
                    categories_of_rawresp.append(
                        {
                            "category": dp,
                            "performance": "",
                            "careerDevelopment": "",
                        }
                    )
            serialized_raw_response.data[0]["data"][0]["employeeCategories"] = (
                categories_of_rawresp
            )
            return serialized_raw_response.data
        # if there are datapoints but no raw response, means that we need to initilize categories
        if dps and not serialized_raw_response.data:
            for category in dps:
                response["employeeCategories"].append(
                    {
                        "category": category,
                        "performance": "",
                        "careerDevelopment": "",
                    }
                )
            return [{"data": response}]

        if not dps and not serialized_raw_response.data:
            return [{"data": response}]
    except Exception as e:
        logger.error(
            f"the following exception occrured for the get field groups > from the function extract_from_diversity_employee : {e} "
        )
