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
