from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)


class WasteSignificantSpillAnalyze(APIView):
    """
    Analyze the data for waste significant spills
    Returns a dictionary of the data
    Calculates the total waste significant spills for the given period
    Uses the raw data from the database, Stores it in init so that it can be used by other functions
    """

    def __init__(self):
        super().__init__()
        self.slugs = {
            0: "gri_environment_waste_significant_spills_306_3b_3c_q1",
        }
        self.raw_data = None

    def set_data_points(self):
        self.data_points = (
            DataPoint.objects.filter(path__slug__in=list(self.slugs.values()))
            .filter(client_id=self.request.user.client.id)
            .filter(
                get_raw_response_filters(
                    corporate=self.corporate, organisation=self.organisation
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
        )

    def set_raw_data(self):
        self.raw_data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[0])
        )

    def total_number_and_volume_by_material(self):
        data_point = self.raw_data
        data_by_material = {}

        for data in data_point:
            unit = data["Unit"]
            material = data["Material"]
            volume = float(data["VolumeofSpill"])
            if unit in data_by_material:
                data_by_material[unit]["volume_of_spills"] += volume
            else:
                data_by_material[unit] = {
                    "material": material,
                    "volume_of_spills": volume,
                    "unit": unit,
                }
        result = list(data_by_material.values())
        return result

    def total_number_and_volume_by_location(self):
        data_point = self.raw_data
        data_by_location = {}
        for data in data_point:
            location = data["Location"]
            unit = data["Unit"]
            volume = float(data["VolumeofSpill"])
            key = (location, unit)
            if location and unit in data_by_location:
                data_by_location[location]["volume_of_spills"] += volume
            else:
                data_by_location[key] = {
                    "location": location,
                    "volume_of_spills": volume,
                    "unit": unit,
                }
        result = list(data_by_location.values())
        return result

    def total_number_and_volume_significant_spills(self):
        data_point = self.raw_data
        data_by_spills = {}
        for data in data_point:
            is_spill = data["SpillSignificant"]
            if is_spill == "Yes":
                unit = data["Unit"]
                volume = float(data["VolumeofSpill"])
                number_of_significant_spills = 1
                if unit in data_by_spills:
                    data_by_spills[unit]["volume_of_spills"] += volume
                    data_by_spills[unit]["number_of_significant_spills"] += (
                        number_of_significant_spills
                    )
                else:
                    data_by_spills[unit] = {
                        "number_of_significant_spills": number_of_significant_spills,
                        "volume_of_spills": volume,
                        "unit": unit,
                    }
        result = list(data_by_spills.values())
        return result

    def get(self, request, *args, **kwargs):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        if (
            self.corporate
        ):  # Using this to get only corporate data and not organisation data
            self.organisation = None
        self.set_data_points()
        self.set_raw_data()
        result = {
            # Table 1 306-3b by material
            "total_number_and_volume_by_material": self.total_number_and_volume_by_material(),
            # Table 2 306-3b by location
            "total_number_and_volume_by_location": self.total_number_and_volume_by_location(),
            # Table 3 306-3a by significant spills
            "total_number_and_volume_significant_spills": self.total_number_and_volume_significant_spills(),
        }
        return Response(result, status=status.HTTP_200_OK)
