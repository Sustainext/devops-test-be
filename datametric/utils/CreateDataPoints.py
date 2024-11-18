from datametric.models import RawResponse, DataPoint, DataMetric, EmissionAnalysis
from django.db.models import prefetch_related_objects
from datametric.utils.signal_utilities import (
    process_raw_response_data,
)
from datametric.utils.signal_utilities import climatiq_data_creation
from analysis.utils.analysis_data_maker import create_analysis_data
from datametric.utils.PathsForDataPoints import (
    type1_paths,
    type2_paths,
    type3_paths,
    type4_path,
)
from logging import getLogger

logger = getLogger("error.log")


class CreateDataPointsClass:

    def __init__(self, json_obj, path, raw_response, data_metrics):
        self.json_obj = json_obj
        self.path = path
        self.raw_response = raw_response
        self.data_metrics = data_metrics

    def list_data_points(self, key, value, index):
        # Check if it's a list of strings or list of dictionaries
        if all(isinstance(item, str) for item in value):
            # If it's a list of strings, pass {key: value}
            process_raw_response_data(
                data_point_dict={key: value},
                data_metrics=self.data_metrics,
                index=index,
                raw_response=self.raw_response,
            )
        elif all(isinstance(item, dict) for item in value):
            # If it's a list of dictionaries, iterate through each dictionary
            for dup_index, item in enumerate(value):
                process_raw_response_data(
                    data_point_dict=item,
                    data_metrics=self.data_metrics,
                    index=dup_index,
                    raw_response=self.raw_response,
                )
        else:
            # Handle mixed or unsupported lists, you can add additional logic here
            logger.error(
                f"File : CreateDataPoints.py > Unhandled list type for key: {key} with value type: {type(value)}"
            )

    def create_data_points_for_raw_response(self):

        if self.path.slug in type1_paths:
            for index, outer_dict in enumerate(self.json_obj):
                for key, value in outer_dict.items():
                    if isinstance(value, dict):

                        # If the value is a dictionary, pass it as data_point_dict with value.items()
                        process_raw_response_data(
                            data_point_dict=value.items(),
                            data_metrics=self.data_metrics,
                            index=index,
                            raw_response=self.raw_response,
                        )
                    elif isinstance(value, list):
                        # Check if it's a list of strings or list of dictionaries
                        self.list_data_points(key, value, index)

                    elif isinstance(value, str):
                        # If it's a string, pass {key: value}
                        process_raw_response_data(
                            data_point_dict={key: value},
                            data_metrics=self.data_metrics,
                            index=index,
                            raw_response=self.raw_response,
                        )
                    else:
                        # Handle other types if needed
                        logger.error(
                            f"File : CreateDataPoints.py > Unhandled data type for key: {key} with value type: {type(value)}"
                        )
        elif self.path.slug in type2_paths:
            for index, outer_dict in enumerate(self.json_obj):
                for dup_index, inner_dict in enumerate(outer_dict.values()):
                    process_raw_response_data(
                        data_point_dict=inner_dict,
                        data_metrics=self.data_metrics,
                        index=dup_index,
                        raw_response=self.raw_response,
                    )
        elif self.path.slug in type3_paths:
            for index, outer_dict in enumerate(self.json_obj):
                for key, value in outer_dict.items():
                    if isinstance(value, list):
                        process_raw_response_data(
                            data_point_dict={key: value},
                            data_metrics=self.data_metrics,
                            index=index,
                            raw_response=self.raw_response,
                        )
        elif self.path.slug in type4_path:
            for index, outer_dict in enumerate(self.json_obj):
                for dup_index, (key, value) in enumerate(outer_dict.items()):
                    for inner_key, inner_value in value.items():
                        if isinstance(inner_value, list):
                            process_raw_response_data(
                                data_point_dict={inner_key: inner_value},
                                data_metrics=self.data_metrics,
                                index=dup_index,
                                raw_response=self.raw_response,
                            )
                        elif isinstance(inner_value, dict):
                            process_raw_response_data(
                                data_point_dict=inner_value,
                                data_metrics=self.data_metrics,
                                index=dup_index,
                                raw_response=self.raw_response,
                            )
                        elif isinstance(inner_value, str):
                            process_raw_response_data(
                                data_point_dict={inner_key: inner_value},
                                data_metrics=self.data_metrics,
                                index=dup_index,
                                raw_response=self.raw_response,
                            )
                        else:
                            logger.error(
                                f"File : CreateDataPoints.py > Unhandled data type for key: {key} with value type: {type(value)}"
                            )
