from collections import defaultdict
from common.utils.data_point_cache import get_data_point_cache
from datametric.models import DataPoint


def collect_data_by_raw_response_and_index(data_points):
    # Create a dictionary where the key is raw_response and the value is another dictionary
    # which maps index to a dictionary of data_metric and value pairs
    raw_response_index_map = defaultdict(dict)
    if isinstance(data_points,list):
        data_points_ids = data_points
    else:
        data_points_ids = [dp.id for dp in data_points.only("id")]
    # Iterate over the list of data points
    for id in data_points_ids:
        # Get the data point from cache if it exists
        data_point_dictionary = get_data_point_cache(id)
        raw_response = data_point_dictionary["raw_response_id"]
        index = data_point_dictionary["index"]
        data_metric = data_point_dictionary["data_metric_name"]
        value = data_point_dictionary["value"]

        # Directly store the data_metric and value for the combination of raw_response and index
        raw_response_index_map[(raw_response, index)][data_metric] = value

    # Convert the defaultdict values into a list of dictionaries (the collected data)
    return list(raw_response_index_map.values())


def collect_data_segregated_by_location(data_points):
    # Dictionary to store data grouped by location and then by raw_response and index
    location_grouped_data = defaultdict(lambda: defaultdict(dict))
    if isinstance(data_points,list):
        data_points_ids = data_points
    else:
        data_points_ids = [dp.id for dp in data_points.only("id")]


    for id in data_points_ids:
        data_point_dictionary = get_data_point_cache(id)
        raw_response = data_point_dictionary["raw_response_id"]
        index = data_point_dictionary["index"]
        data_metric = data_point_dictionary["data_metric_name"]
        value = data_point_dictionary["value"]
        location = data_point_dictionary["location_name"]

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
    if isinstance(data_points,list):
        data_points_ids = data_points
    else:
        data_points_ids = [dp.id for dp in data_points.only("id")]

    # Iterate over the list of data points
    for id in data_points_ids:
        data_point_dictionary = get_data_point_cache(id)
        raw_response = data_point_dictionary["raw_response_id"]
        index = data_point_dictionary["index"]
        data_metric = data_point_dictionary["data_metric_name"]
        value = data_point_dictionary["value"]
        location = data_point_dictionary["location_name"]

        # Store the data_metric and its value for the current location, raw_response and index
        location_grouped_data[location][(raw_response, index)][data_metric] = value

    # Convert to dictionary where keys are locations and values are lists of data points
    for location in location_grouped_data:
        # Get all data points for this location
        location_data = list(location_grouped_data[location].values())
        result[location] = location_data

    return result

def collect_data_and_differentiate_by_location(data_points):
    # Dictionary to store data grouped by raw_response and index (ignoring location for grouping)
    raw_response_index_map = defaultdict(dict)
    if isinstance(data_points,list):
        data_points_ids = data_points
    else:
        data_points_ids = [dp.id for dp in data_points.only("id")]


    # Set to store unique locations
    unique_locations = set()

    # Iterate over the list of data points
    for id in data_points_ids:
        data_point_dictionary = get_data_point_cache(id)
        raw_response = data_point_dictionary["raw_response_id"]
        index = data_point_dictionary["index"]
        data_metric = data_point_dictionary["data_metric_name"]
        value = data_point_dictionary["value"]
        location = data_point_dictionary["location_name"]

        # Store the data_metric and its value for the current raw_response and index
        raw_response_index_map[(raw_response, index)][data_metric] = value

        # Collect unique locations
        unique_locations.add(location)

    # Convert raw_response_index_map to a list of dictionaries (ignoring location for grouping)
    grouped_data = list(raw_response_index_map.values())

    # Return the grouped data and the list of unique locations
    response_data = {"data": grouped_data, "locations": list(unique_locations)}

    return response_data
