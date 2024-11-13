from datametric.utils.analyse import safe_integer_divide


def get_community_engagement_analysis(raw_responses, slugs):
    """
    This function is used to calculate the community engagement data.
    """
    local_data = [
        raw_response.data for raw_response in raw_responses.filter(path__slug=slugs[0])
    ]
    print(slugs[0])
    response_data = {
        "Social impact assessments": 0,
        "Environmental impact assessments": 0,
        "Public disclosure": 0,
        "Community development programs": 0,
        "Stakeholder engagement plans": 0,
        "Local community consultation committees": 0,
        "Works councils, occupational health and safety committees": 0,
        "Community grievance processes": 0,
    }
    sum_of_total_operation = sum(
        [
            sum(int(item["totaloperations"]) for item in sublist)
            for sublist in local_data
        ]
    )

    for each_month_data in local_data:
        response_data["Social impact assessments"] += int(
            each_month_data[0]["operations"]
        )
        response_data["Environmental impact assessments"] += int(
            each_month_data[1]["operations"]
        )
        response_data["Public disclosure"] += int(each_month_data[2]["operations"])
        response_data["Community development programs"] += int(
            each_month_data[3]["operations"]
        )
        response_data["Stakeholder engagement plans"] += int(
            each_month_data[4]["operations"]
        )
        response_data["Local community consultation committees"] += int(
            each_month_data[5]["operations"]
        )
        response_data[
            "Works councils, occupational health and safety committees"
        ] += int(each_month_data[6]["operations"])
        response_data["Community grievance processes"] += int(
            each_month_data[7]["operations"]
        )

    # Calculate the percentage of operations
    for key, value in response_data.items():
        response_data[key] = safe_integer_divide(value, sum_of_total_operation)

    # Prepare the response data list
    response_data_list = [
        {
            "": key,
            "Percentage of operations implemented by engaging local communities": value,
        }
        for key, value in response_data.items()
    ]

    return response_data_list
