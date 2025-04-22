from rest_framework.views import APIView
from rest_framework.response import Response
from apps.optimize.models.SelectedAvtivityModel import SelectedActivity
from apps.optimize.models.BusinessMetric import BusinessMetric
import requests
import os
import json
from django.shortcuts import get_object_or_404
from apps.optimize.models.OptimizeScenario import Scenerio
from decimal import Decimal
from django.forms.models import model_to_dict


class CalculateClimatiqResult(APIView):
    """
    This class defines the view for calculating the result of Climatiq API.
    It takes the selected activities and calculates the result using the Climatiq API.
    """

    def construct_emission_req(
        self, activity_id, unit_type, value1, unit1, value2=None, unit2=None
    ):
        emission_req = {
            "emission_factor": {"activity_id": activity_id, "data_version": "^16"},
            "parameters": {},
        }

        unit_type = unit_type.lower()

        param_structures = {
            "area": {"area": value1, "area_unit": unit1},
            "areaovertime": {
                "area": value1,
                "area_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
            "containeroverdistance": {
                "twenty_foot_equivalent": value2,
                "distance": value1,
                "distance_unit": unit2,
            },
            "data": {"data": value1, "data_unit": unit1},
            "dataovertime": {
                "data": value1,
                "data_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
            "distance": {"distance": value1, "distance_unit": unit1},
            "distanceovertime": {
                "distance": value1,
                "distance_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
            "energy": {"energy": value1, "energy_unit": unit1},
            "money": {"money": value1, "money_unit": unit1},
            "number": {"number": int(value1)},
            "numberovertime": {"number": value1, "time": value2, "time_unit": unit2},
            "passengeroverdistance": {
                "passengers": int(value1),
                "distance": value2,
                "distance_unit": unit2,
            },
            "time": {"time": value1, "time_unit": unit1},
            "volume": {"volume": value1, "volume_unit": unit1},
            "weight": {"weight": value1, "weight_unit": unit1},
            "weightoverdistance": {
                "weight": value1,
                "weight_unit": unit1,
                "distance": value2,
                "distance_unit": unit2,
            },
            "weightovertime": {
                "weight": value1,
                "weight_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
        }

        if unit_type in param_structures:
            emission_req["parameters"] = param_structures[unit_type]

        return emission_req

    def calculate_result(self, payload):
        """
        This method calculates the result of Climatiq API.
        It takes the payload and calculates the result using the Climatiq API.
        """
        CLIMATIQ_AUTH_TOKEN: str | None = os.getenv("CLIMATIQ_AUTH_TOKEN")
        headers = {"Authorization": f"Bearer {CLIMATIQ_AUTH_TOKEN}"}
        batch_size = 100
        for i in range(0, len(payload), batch_size):
            batch_payload = payload[i : i + batch_size]
            response = requests.request(
                "POST",
                url="https://api.climatiq.io/data/v1/estimate/batch",
                data=json.dumps(batch_payload, default=str),
                headers=headers,
            )
        return response.json()

    def intensity(self, base_year_consumption, business_metric_abs_value):
        """Function to calculate the intensity based on the selected activities and business metrics"""
        """Intensity = base_year_consumption/business_metric_abs_value"""
        return

    def get(self, request, scenario_id):
        """
        This method handles the GET request for calculating the result of Climatiq API.
        It takes the selected activities and calculates the result using the Climatiq API.
        """
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        selected_activities = SelectedActivity.objects.filter(scenario=scenario)
        business_metrics = BusinessMetric.objects.get(scenario=scenario)
        if business_metrics.fte:
            fte_data = business_metrics.fte_data
            fte_abs_value = Decimal(fte_data["abs_value"])
            fte_percentage_change = fte_data["percentage_change"]
            print(fte_percentage_change)
        else:
            fte_abs_value = None

        if business_metrics.area:
            area_data = business_metrics.area_data
            area_abs_value = Decimal(area_data["abs_value"])
        else:
            area_abs_value = None

        if business_metrics.revenue:
            revenue_data = business_metrics.revenue_data
            revenue_abs_value = Decimal(revenue_data["abs_value"])
        else:
            revenue_abs_value = None

        if business_metrics.production_volume:
            production_volume_data = business_metrics.production_volume_data
            production_volume_abs_value = Decimal(production_volume_data["abs_value"])
        else:
            production_volume_abs_value = None

        print(
            fte_abs_value,
            area_abs_value,
            revenue_abs_value,
            production_volume_abs_value,
        )
        climatiq_payload = []
        for activity in selected_activities:
            intensity = activity.quantity / fte_abs_value
            print(intensity)

            for year, percentage in fte_percentage_change.items():
                adjusted_fte_abs = fte_abs_value * (
                    Decimal(1) + Decimal(percentage) / Decimal(100)
                )
                adjusted_quantity = adjusted_fte_abs * intensity
                print(f"Quantity before percentage_change: {adjusted_quantity}")
                adjusted_quantity = adjusted_quantity * (
                    Decimal(1)
                    + Decimal(activity.percentage_change[year]) / Decimal(100)
                )
                print(
                    f"intensity:{intensity},{adjusted_fte_abs},{adjusted_quantity},{year},{activity.percentage_change[year]}"
                )

                climatiq_payload.append(
                    {
                        "emission_factor": {
                            "activity_id": activity.activity_id,
                            "data_version": f"^{os.getenv('CLIMATIQ_DATA_VERSION')}",
                        },
                        "parameters": {
                            "energy": float(round(adjusted_quantity, 4)),
                            "energy_unit": activity.unit,
                        },
                    }
                )
                intensity = adjusted_quantity / adjusted_fte_abs
                fte_abs_value = adjusted_fte_abs
        # climatiq_result = self.calculate_result(climatiq_payload)

        result = {
            "selected_activities": selected_activities.values(),
            "business_metrics": model_to_dict(business_metrics),
            "climatiq_payload": climatiq_payload,
            # "climatiq_result": climatiq_result,
        }
        return Response(result)
