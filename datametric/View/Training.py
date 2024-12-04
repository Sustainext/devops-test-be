from datametric.models import DataPoint, RawResponse

"""
Employment > Diversity of Employee : Is where we have to get the categories from
Training and Development > Employee Performance and career development: is where we show the cattegories
"""


def get_categories_serilalized_raw_response(resp):
    """
    This function takes in a serialized raw response and returns a list of categories
    """
    categories = {}
    for item in resp:
        if item["category"] not in categories:
            categories.update({item["category"]: ""})
    return categories


def extract_from_diversity_employee(serialized_raw_response, **kwargs):
    # lets say we have already fetched a the categories form employment, then they work update the data.
    # what if they add a new category later?
    # Solution : may be we need to fetch from the raw response everytime??

    # What if they have data, in the present code we are always fetching data and over writing the existing data
    # what if they edit the existing categories
    try:
        resp = {}
        if serialized_raw_response.data:
            resp = serialized_raw_response.data[0]["data"]
            categories = get_categories_serilalized_raw_response(resp)
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

        dps = (
            DataPoint.objects.filter(**kwargs, metric_name="category")
            .values_list("value", flat=True)
            .order_by("id")
        )
        # Check if datapoints are there and if any new categories are added to employement
        if dps and serialized_raw_response.data:
            for dp in dps:
                if dp not in categories:
                    # print(resp)
                    resp.append(
                        {
                            "category": dp,
                            "performance": "",
                            "careerDevelopment": "",
                        }
                    )
            serialized_raw_response.data[0]["data"] = resp
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
            return [response]
    except Exception as e:
        print(e)
