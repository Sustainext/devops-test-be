from collections import defaultdict


def collect_data_by_raw_response_and_index(data_points):
    # Create a dictionary where the key is raw_response and the value is another dictionary
    # which maps index to a dictionary of data_metric and value pairs
    raw_response_index_map = defaultdict(dict)

    # Iterate over the list of data points
    for dp in data_points:
        raw_response = dp.raw_response.id
        index = dp.index
        data_metric = dp.data_metric.name
        value = dp.value

        # Directly store the data_metric and value for the combination of raw_response and index
        raw_response_index_map[(raw_response, index)][data_metric] = value

    # Convert the defaultdict values into a list of dictionaries (the collected data)
    return list(raw_response_index_map.values())


def collect_data_segregated_by_location(data_points):
    # Dictionary to store data grouped by location and then by raw_response and index
    location_grouped_data = defaultdict(lambda: defaultdict(dict))

    # Iterate over the list of data points
    for dp in data_points:
        raw_response = dp.raw_response.id
        index = dp.index
        data_metric = dp.data_metric.name
        value = dp.value
        location = dp.locale.name if dp.locale else None

        # Store the data_metric and its value for the current location, raw_response and index
        location_grouped_data[location][(raw_response, index)][data_metric] = value

    # Convert the nested defaultdict to a list of lists
    result = []

    # Convert each location's data to a list
    for location in location_grouped_data:
        # Get all data points for this location
        location_data = list(location_grouped_data[location].values())
        result.append(location_data)

    return result


def get_location_wise_dictionary_data(data_points):
    # Dictionary to store data grouped by location and then by raw_response and index
    location_grouped_data = defaultdict(lambda: defaultdict(dict))
    result = {}

    # Iterate over the list of data points
    for dp in data_points:
        raw_response = dp.raw_response.id
        index = dp.index
        data_metric = dp.data_metric.name
        value = dp.value
        location = dp.locale.name if dp.locale else None

        # Store the data_metric and its value for the current location, raw_response and index
        location_grouped_data[location][(raw_response, index)][data_metric] = value

    # Convert to dictionary where keys are locations and values are lists of data points
    for location in location_grouped_data:
        # Get all data points for this location
        location_data = list(location_grouped_data[location].values())
        result[location] = location_data

    return result
