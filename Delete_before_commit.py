from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from sustainapp.models import Location
from environmentapp.models.EnergyModels import (
    DirectPurchasedEnergy,
    ConsumedEnergy,
    SelfGenerated,
    EnergySold,
    SMAC,
    SourceOfConversionFactor,
    EnergyConsumedOutsideOrg,
    EnergyIntensity,
    Baseyear,
    ReductionEnergyConsumption,
    ReductionInProductServices,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from collections import defaultdict
from django.http import JsonResponse
from django.db.models import Sum, Case, When, Value, FloatField, Model
from django.db.models.functions import Cast, Round, Coalesce
from django.db.models import F, DecimalField
from decimal import Decimal


def process_energy_data(model, location_id, year, month, fields, renewability=None):
    # group_by_fields :
    conversions = {
        "J": {"GJ": 1e-9, "kWh": 0.00000027778},
        "KJ": {"GJ": 1e-6, "kWh": 0.00027778},
        "Wh": {"GJ": 0.0000036, "kWh": 0.001},
        "KWh": {"GJ": 0.0036, "kWh": 1},
        "GJ": {"GJ": 1, "kWh": 277.78},
        "MMBtu": {"GJ": 1.055056, "kWh": 293.071},
    }

    query = model.objects.filter(location_id=location_id, year=year, month=month)
    if renewability:
        query = query.filter(renewability=renewability)

    converted_quantities = query.annotate(
        quantity_gj=Round(
            Case(
                *[
                    When(unit=unit, then=F("quantity") * values["GJ"])
                    for unit, values in conversions.items()
                ],
                default=F("quantity"),
                output_field=DecimalField(),
            ),
            5,
        ),
        quantity_kwh=Round(
            Case(
                *[
                    When(unit=unit, then=F("quantity") * values["kWh"])
                    for unit, values in conversions.items()
                ],
                default=F("quantity"),
                output_field=DecimalField(),
            ),
            5,
        ),
    )

    # Aggregate data based on dynamic fields
    result = (
        converted_quantities.values(*fields)
        .annotate(
            total_quantity_gj=Sum("quantity_gj"), total_quantity_kwh=Sum("quantity_kwh")
        )
        .order_by(*fields)
    )

    # Calculate the grand total of all converted quantities
    grand_total_gj = converted_quantities.aggregate(
        grand_total_gj=Coalesce(Round(Sum("quantity_gj"), 5), Decimal(0))
    )["grand_total_gj"]

    grand_total_kwh = converted_quantities.aggregate(
        grand_total_kwh=Coalesce(Round(Sum("quantity_kwh"), 5), Decimal(0))
    )["grand_total_kwh"]

    return result, grand_total_gj, grand_total_kwh


class AnalyseEnergyViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        location_id = request.query_params.get("location")
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        if location_id and year and month:

            # energy_intensity_data = process_energy_intensity_data(location_id, year, month)

            models = {
                "ConsumedEnergy": (ConsumedEnergy, ["energy_type", "source"]),
                "DirectPurchasedEnergy": (
                    DirectPurchasedEnergy,
                    ["energy_type", "source", "purpose"],
                ),
                "SelfGenerate": (SelfGenerated, ["energy_type", "source"]),
                "EnergySold": (
                    EnergySold,
                    ["energy_type", "source", "entity_type", "name_of_entity"],
                ),
                "EnergyConsumedOutsideOrg": (
                    EnergyConsumedOutsideOrg,
                    ["energy_type", "purpose"],
                ),
                "ReductionEnergyConsumption": (
                    ReductionEnergyConsumption,
                    [
                        "type_of_intervention",
                        "energy_type_reduced",
                        "energy_reduction",
                        "base_year",
                        "methodology_used",
                    ],
                ),
                "ReductionInProductServices": (
                    ReductionInProductServices,
                    ["product"],
                ),  # -----> Match Repo and repo to one
            }
            response_data = {
                "energy_consumption_within_the_org": {
                    "Non-renewable fuel consumed": 0,
                    "Renewable fuel consumed": 0,
                    "Electricity, heating, cooling, and steam purchased for consumption from renewable sources": 0,
                    "Electricity, heating, cooling, and steam purchased for consumption from non-renewable sources": 0,
                    "Self-generated electricity, heating, cooling, and steam, which are not consumed from renewable source": 0,
                    "Self-generated electricity, heating, cooling, and steam, which are not consumed from non-renewable source": 0,
                    "Electricity, heating, cooling, and steam sold (renewable energy)": 0,
                    "Electricity, heating, cooling, and steam sold (non-renewable energy)": 0,
                    "Total Energy consumption within the org": 0,
                }
            }

            for name, (model, fields) in models.items():

                if name in [
                    "ReductionEnergyConsumption",
                    "ReductionInProductServices",
                    "EnergyConsumedOutsideOrg",
                ]:
                    data, grand_total_gj, grand_total_kwh = process_energy_data(
                        model, location_id, year, month, fields
                    )
                    response_data[name] = {
                        "Details": [
                            {
                                "total_quantity_gj": item["total_quantity_gj"],
                                "units_in_GJ": "GJ",
                                "total_quantity_kwh": item["total_quantity_kwh"],
                                "units_in_kWh": "kWh",
                                **{field: item[field] for field in fields},
                            }
                            for item in data
                        ],
                        "Grand Total GJ": grand_total_gj,
                        "units_in_GJ": "GJ",
                        "Grand Total kWh": grand_total_kwh,
                        "units_in_kWh": "kWh"
                    }
                else:
                    (
                        renewable_data,
                        renewable_grand_total_gj,
                        renewable_grand_total_kwh,
                    ) = process_energy_data(
                        model, location_id, year, month, fields, "Renewable"
                    )
                    (
                        non_renewable_data,
                        non_renewable_grand_total_gj,
                        non_renewable_grand_total_kwh,
                    ) = process_energy_data(
                        model, location_id, year, month, fields, "Non-Renewable"
                    )

                    # defining the logic for Energy consumed within the orgnization
                    if name == "ConsumedEnergy":
                        response_data["energy_consumption_within_the_org"][
                            "Non-renewable fuel consumed"
                        ] = renewable_grand_total_gj
                        response_data["energy_consumption_within_the_org"][
                            "Renewable fuel consumed"
                        ] = non_renewable_grand_total_gj
                    elif name == "DirectPurchasedEnergy":
                        response_data["energy_consumption_within_the_org"][
                            "Electricity, heating, cooling, and steam purchased for consumption from renewable sources"
                        ] = renewable_grand_total_gj
                        response_data["energy_consumption_within_the_org"][
                            "Electricity, heating, cooling, and steam purchased for consumption from non-renewable sources"
                        ] = non_renewable_grand_total_gj
                    elif name == "SelfGenerate":
                        response_data["energy_consumption_within_the_org"][
                            "Self-generated electricity, heating, cooling, and steam, which are not consumed from renewable source"
                        ] = renewable_grand_total_gj
                        response_data["energy_consumption_within_the_org"][
                            "Self-generated electricity, heating, cooling, and steam, which are not consumed from non-renewable source"
                        ] = non_renewable_grand_total_gj
                    else:
                        response_data["energy_consumption_within_the_org"][
                            "Electricity, heating, cooling, and steam sold (renewable energy)"
                        ] = renewable_grand_total_gj
                        response_data["energy_consumption_within_the_org"][
                            "Electricity, heating, cooling, and steam sold (non-renewable energy)"
                        ] = non_renewable_grand_total_gj
                        response_data["energy_consumption_within_the_org"][
                            "Total Energy consumption within the org"
                        ] = round(
                            response_data["energy_consumption_within_the_org"][
                                "Non-renewable fuel consumed"
                            ]
                            + response_data["energy_consumption_within_the_org"][
                                "Renewable fuel consumed"
                            ]
                            + response_data["energy_consumption_within_the_org"][
                                "Electricity, heating, cooling, and steam purchased for consumption from renewable sources"
                            ]
                            + response_data["energy_consumption_within_the_org"][
                                "Electricity, heating, cooling, and steam purchased for consumption from non-renewable sources"
                            ]
                            + response_data["energy_consumption_within_the_org"][
                                "Self-generated electricity, heating, cooling, and steam, which are not consumed from renewable source"
                            ]
                            + response_data["energy_consumption_within_the_org"][
                                "Self-generated electricity, heating, cooling, and steam, which are not consumed from non-renewable source"
                            ]
                            - response_data["energy_consumption_within_the_org"][
                                "Electricity, heating, cooling, and steam sold (renewable energy)"
                            ]
                            - response_data["energy_consumption_within_the_org"][
                                "Electricity, heating, cooling, and steam sold (non-renewable energy)"
                            ],
                            5,
                        )

                    # Ends here
                    response_data[name] = {
                        "Renewable": {
                            "Details": [
                                {
                                    "total_quantity_gj": item["total_quantity_gj"],
                                    "units": "GJ",
                                    # 'total_quantity_kwh': item['total_quantity_kwh'],
                                    # 'units_in_kWh': 'kWh',
                                    **{field: item[field] for field in fields},
                                }
                                for item in renewable_data
                            ],
                            "Grand Total GJ": renewable_grand_total_gj,
                            "units_in_GJ": "GJ"
                            # 'Grand Total kWh': renewable_grand_total_kwh
                        },
                        "Non-Renewable": {
                            "Details": [
                                {
                                    "total_quantity_gj": item["total_quantity_gj"],
                                    "units_in_GJ": "GJ",
                                    # "total_quantity_kwh": item["total_quantity_kwh"],
                                    # "units_in_kWh": "kWh",
                                    **{field: item[field] for field in fields},
                                }
                                for item in non_renewable_data
                            ],
                            "Grand Total GJ": non_renewable_grand_total_gj,
                            "units_in_GJ": "GJ"
                            # "Grand Total kWh": non_renewable_grand_total_kwh,
                        },
                    }

            total_energy_consumption = response_data[
                "energy_consumption_within_the_org"
            ]["Total Energy consumption within the org"]

            # Aggregate metric quantities for EnergyIntensity
            energy_intensity_aggregates = (
                EnergyIntensity.objects.filter(
                    location_id=location_id, year=year, month=month
                )
                .values("org_metric", "metric_unit")
                .annotate(total_metric_quantity=Sum("metric_quantity"))
                .order_by("org_metric")
            )

            # Calculate intensity per aggregated metric unit
            intensity_response = []
            for aggregate in energy_intensity_aggregates:
                total_metric_quantity = aggregate["total_metric_quantity"]
                intensity_per_unit_gj = total_energy_consumption / total_metric_quantity
                intensity_per_unit_kwh = intensity_per_unit_gj * Decimal(277.777778)

                intensity_response.append(
                    {
                        # 'energy_type': aggregate['energy_type'],
                        "org_metric": aggregate["org_metric"],
                        "energy_quantity": total_energy_consumption,
                        "intensity_per_unit_gj": f"{intensity_per_unit_gj:.5f}",
                        "metric_unit1": "GJ/" + aggregate["metric_unit"],
                        "intensity_per_unit_kwh": f"{intensity_per_unit_kwh:.5f}",
                        "metric_unit2": "KWh/" + aggregate["metric_unit"],
                        # 'intensity_per_unit_gj': f"{intensity_per_unit_gj:.5f} GJ/{aggregate['metric_unit']}"
                        # 'intensity_per_unit_kwh': f"{intensity_per_unit_kwh:.5f} kWh/{aggregate['metric_unit']}",
                    }
                )

            response_data["EnergyIntensity"] = intensity_response

            return Response({"Energy Data": response_data})
        else:
            return JsonResponse({"error": "Missing parameters"}, status=400)    
