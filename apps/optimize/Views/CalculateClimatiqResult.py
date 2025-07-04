from rest_framework.views import APIView
from rest_framework.response import Response
from apps.optimize.models.SelectedActivityModel import SelectedActivity
from apps.optimize.models.BusinessMetric import BusinessMetric
import requests
import os
import json
from django.shortcuts import get_object_or_404
from apps.optimize.models.OptimizeScenario import Scenerio
from decimal import Decimal, InvalidOperation
from apps.optimize.models.CalculatedResult import CalculatedResult
from apps.optimize.Service.emission_data_service import EmissionDataService
from django.db import transaction
# from django.forms.models import model_to_dict  #Keeping it here untill testing is completed


class CalculateClimatiqResult(APIView):
    """
    This class defines the view for calculating the result of Climatiq API.
    It takes the selected activities and calculates the result using the Climatiq API.
    """

    def calculate_result(self, payload):
        """
        This method calculates the result of Climatiq API.
        It sends the payload in batches and returns the combined result.
        """
        CLIMATIQ_AUTH_TOKEN: str | None = os.getenv("CLIMATIQ_AUTH_TOKEN")
        headers = {"Authorization": f"Bearer {CLIMATIQ_AUTH_TOKEN}"}
        batch_size = 100
        all_results = []

        for i in range(0, len(payload), batch_size):
            batch_payload = payload[i : i + batch_size]
            response = requests.post(
                url="https://api.climatiq.io/data/v1/estimate/batch",
                data=json.dumps(batch_payload, default=str),
                headers=headers,
            )
            batch_results = response.json().get("results", [])
            all_results.extend(batch_results)

        return {"results": all_results}

    def get_adjusted_quantity(
        self,
        base_quantity,
        base_value,
        percentage_change_map,
        activity_percentage_change,
        base_quantity2=None,
    ):
        """
        Recalculates adjusted quantity and optional second quantity based on metric and activity change.
        """
        yearly_data = []
        try:
            intensity = Decimal(base_quantity) / Decimal(base_value)
        except (InvalidOperation, ZeroDivisionError):
            intensity = Decimal(0)

        if base_quantity2 is not None:
            intensity2 = base_quantity2 / base_value if base_value != 0 else 0
        else:
            intensity2 = None

        for year, pct_change in percentage_change_map.items():
            adjusted_base = base_value * (
                Decimal(1) + Decimal(pct_change) / Decimal(100)
            )
            adjusted_quantity = adjusted_base * intensity
            adjusted_quantity *= Decimal(1) + Decimal(
                activity_percentage_change.get(year, 0)
            ) / Decimal(100)

            if intensity2 is not None:
                adjusted_quantity2 = adjusted_base * intensity2
                adjusted_quantity2 *= Decimal(1) + Decimal(
                    activity_percentage_change.get(year, 0)
                ) / Decimal(100)
            else:
                adjusted_quantity2 = None

            yearly_data.append(
                {
                    "year": year,
                    "adjusted_quantity": adjusted_quantity,
                    "adjusted_quantity2": adjusted_quantity2,
                    "adjusted_base": adjusted_base,
                    "intensity": intensity,
                }
            )

            intensity = (adjusted_quantity / adjusted_base) if adjusted_base else 0
            if intensity2 is not None:
                intensity2 = adjusted_quantity2 / adjusted_base if adjusted_base else 0
            base_value = adjusted_base

        return yearly_data

    def generate_payload(
        self, selected_activities, base_value, percentage_change_map, metric_name
    ):
        """Generate Climatiq payload using dynamic param structure based on unit_type."""
        payload = []

        param_structures = {
            "area": lambda v1, u1, v2=None, u2=None: {"area": v1, "area_unit": u1},
            "areaovertime": lambda v1, u1, v2, u2: {
                "area": v1,
                "area_unit": u1,
                "time": v2,
                "time_unit": u2,
            },
            "containeroverdistance": lambda v1, u1, v2, u2: {
                "distance": v1,
                "distance_unit": u2,
                "twenty_foot_equivalent": int(v2),
            },
            "data": lambda v1, u1, v2=None, u2=None: {"data": v1, "data_unit": u1},
            "dataovertime": lambda v1, u1, v2, u2: {
                "data": v1,
                "data_unit": u1,
                "time": v2,
                "time_unit": u2,
            },
            "distance": lambda v1, u1, v2=None, u2=None: {
                "distance": v1,
                "distance_unit": u1,
            },
            "distanceovertime": lambda v1, u1, v2, u2: {
                "distance": v1,
                "distance_unit": u1,
                "time": v2,
                "time_unit": u2,
            },
            "energy": lambda v1, u1, v2=None, u2=None: {
                "energy": v1,
                "energy_unit": u1,
            },
            "money": lambda v1, u1, v2=None, u2=None: {"money": v1, "money_unit": u1},
            "number": lambda v1, u1=None, v2=None, u2=None: {"number": int(v1)},
            "numberovertime": lambda v1, u1, v2, u2: {
                "number": v1,
                "time": v2,
                "time_unit": u2,
            },
            "passengeroverdistance": lambda v1, u1, v2, u2: {
                "passengers": int(v1),
                "distance": v2,
                "distance_unit": u2,
            },
            "time": lambda v1, u1, v2=None, u2=None: {"time": v1, "time_unit": u1},
            "volume": lambda v1, u1, v2=None, u2=None: {
                "volume": v1,
                "volume_unit": u1,
            },
            "weight": lambda v1, u1, v2=None, u2=None: {
                "weight": v1,
                "weight_unit": u1,
            },
            "weightoverdistance": lambda v1, u1, v2, u2: {
                "weight": v1,
                "weight_unit": u1,
                "distance": v2,
                "distance_unit": u2,
            },
            "weightovertime": lambda v1, u1, v2, u2: {
                "weight": v1,
                "weight_unit": u1,
                "time": v2,
                "time_unit": u2,
            },
        }

        for activity in selected_activities:
            unit_type_key = activity.unit_type.lower()
            generate_params = param_structures.get(unit_type_key)

            if not generate_params:
                raise ValueError(f"Unsupported unit_type: {activity.unit_type}")

            yearly_data = self.get_adjusted_quantity(
                base_quantity=Decimal(activity.quantity),
                base_value=base_value,
                percentage_change_map=percentage_change_map,
                activity_percentage_change=activity.percentage_change,
                base_quantity2=Decimal(activity.quantity2)
                if activity.quantity2
                else None,
            )

            for data in yearly_data:
                year = data["year"]
                activity_id = activity.activity_id

                if activity.activity_change and activity.changes_in_activity:
                    year_change = activity.changes_in_activity.get(str(year))
                    if year_change:
                        activity_id = year_change.get("activity_id", activity_id)

                v1 = float(round(data["adjusted_quantity"], 4))
                u1 = activity.unit
                v2 = (
                    float(round(data["adjusted_quantity2"], 4))
                    if data["adjusted_quantity2"]
                    else 0
                )
                u2 = (
                    activity.unit2
                    if hasattr(activity, "unit2") and activity.unit2
                    else 0
                )

                parameters = generate_params(v1, u1, v2, u2)

                payload.append(
                    {
                        "metric": metric_name,
                        "scope": activity.scope,
                        "category": activity.category,
                        "sub_category": activity.sub_category,
                        "unit_type": unit_type_key,
                        "activity_name": activity.activity_name,
                        "uuid": str(activity.uuid),
                        "year": data["year"],
                        "emission_factor": {
                            "activity_id": activity_id,
                            "data_version": f"^{os.getenv('CLIMATIQ_DATA_VERSION')}",
                        },
                        "parameters": parameters,
                    }
                )

        return payload

    def get(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        selected_activities = SelectedActivity.objects.filter(scenario=scenario)
        business_metrics = BusinessMetric.objects.get(scenario=scenario)

        full_payload = []
        true_metrics = []

        # FTE metric
        if business_metrics.fte and business_metrics.fte_data:
            fte_abs = Decimal(business_metrics.fte_data["abs_value"])
            fte_pct_change = business_metrics.fte_data.get("percentage_change", {})
            full_payload += self.generate_payload(
                selected_activities, fte_abs, fte_pct_change, "fte"
            )
            true_metrics.append("fte")

        # Area metric
        if business_metrics.area and business_metrics.area_data:
            area_abs = Decimal(business_metrics.area_data["abs_value"])
            area_pct_change = business_metrics.area_data.get("percentage_change", {})
            full_payload += self.generate_payload(
                selected_activities, area_abs, area_pct_change, "area"
            )
            true_metrics.append("area")

        # Revenue metric
        if business_metrics.revenue and business_metrics.revenue_data:
            revenue_abs = Decimal(business_metrics.revenue_data["abs_value"])
            revenue_pct_change = business_metrics.revenue_data.get(
                "percentage_change", {}
            )
            full_payload += self.generate_payload(
                selected_activities, revenue_abs, revenue_pct_change, "revenue"
            )
            true_metrics.append("revenue")

        # Production volume metric
        if (
            business_metrics.production_volume
            and business_metrics.production_volume_data
        ):
            prod_abs = Decimal(business_metrics.production_volume_data["abs_value"])
            prod_pct_change = business_metrics.production_volume_data.get(
                "percentage_change", {}
            )
            full_payload += self.generate_payload(
                selected_activities, prod_abs, prod_pct_change, "production_volume"
            )
            true_metrics.append("production_volume")

        climatiq_result = self.calculate_result(full_payload)

        emission_data = EmissionDataService().get_emission_data(request, scenario_id)

        bulk_results = []

        for payload, result in zip(full_payload, climatiq_result["results"]):
            uuid = payload["uuid"]
            year = payload["year"]
            scope = payload["scope"]
            category = payload["category"]
            sub_category = payload["sub_category"]
            metric = payload["metric"]
            activity_id = payload["emission_factor"]["activity_id"]

            activity_name = payload["activity_name"]

            bulk_results.append(
                CalculatedResult(
                    scenario=scenario,
                    uuid=uuid,
                    year=year,
                    scope=scope,
                    category=category,
                    sub_category=sub_category,
                    activity_id=activity_id,
                    activity_name=activity_name,
                    metric=metric,
                    result=result,
                )
            )

        for data in emission_data:
            uuid = str(data.get("uuid"))
            scope = data.get("scope")
            category = data.get("category")
            sub_category = data.get("sub_category")
            activity_id = data.get("activity_id")
            activity_name = data.get("activity_name")
            result = {"co2e": float(data["co2e_total"])}
            year = scenario.base_year

            for metric in true_metrics:
                bulk_results.append(
                    CalculatedResult(
                        scenario=scenario,
                        uuid=uuid,
                        year=year,
                        scope=scope,
                        category=category,
                        sub_category=sub_category,
                        activity_id=activity_id,
                        activity_name=activity_name,
                        metric=metric,
                        result=result,
                    )
                )
        try:
            with transaction.atomic():
                CalculatedResult.objects.filter(scenario=scenario).delete()
                CalculatedResult.objects.bulk_create(bulk_results)
        except Exception as e:
            print(e)
            # TODO: add loggin here later

        result = {
            # "selected_activities": selected_activities.values(),  #Keeping it here untill testing is completed
            # "business_metrics": model_to_dict(business_metrics),  #Keeping it here untill testing is completed
            "climatiq_payload": full_payload,  # Keeping it here untill testing is completed
            "climatiq_result": climatiq_result,
        }

        return Response(result)
