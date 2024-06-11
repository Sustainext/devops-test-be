import json
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import Corporateentity, AnalysisData2, Report, Location
from rest_framework import viewsets, generics
from sustainapp.serializers import ReportSerializer
from rest_framework.permissions import AllowAny
from datametric.models import RawResponse
from sustainapp.Serializers.GHGReportSerializer import (
    CheckReportDataSerializer,
    GHGReportRawResponseSerializer,
    ScopeDataSerializer,
)
from rest_framework.views import APIView
from datametric.serializers import RawResponseSerializer
from collections import defaultdict


def handle_none(value):
    return value if value is not None else 0


def calculate_total(queryset):
    return queryset.aggregate(total=Sum("co2e"))


# def get_data_for_ghg_report(year, month, corporate_id, report_id, client_id):
#     print("Function Triggered")
#     print("Year:", year)
#     print("Month:", month)
#     try:
#         # Retrieve the Corporateentity instance
#         corporate = Corporateentity.objects.get(id=corporate_id)

#         # Access all related Location objects using the related_name 'locations'
#         locations = corporate.location.all()

#         if not locations.exists():
#             return Response(
#                 {"message": "No locations found for this corporate entity."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         total_emission_value = 0
#         scope_arr = []
#         category_arr = []
#         location_arr = []

#         # Process each location
#         for location in locations:
#             # Filter RawResponse data for the specified year, month, and location
#             raw_responses = RawResponse.objects.filter(
#                 year=year, month=month, location=location.name
#             )

#             if not raw_responses.exists():
#                 continue  # Skip if no data is found for this location

#             for raw_response in raw_responses:
#                 data = raw_response.data
#                 for item in data:
#                     emission = item.get("Emission", {})
#                     quantity = int(emission.get("Quantity", 0))
#                     total_emission_value += quantity

#                     scope_arr.append(
#                         {
#                             "scope_name": raw_response.path.split("-")[-1],
#                             "total_co2e": round(quantity / 1000, 2),
#                             "contribution_scope": 0,  # Placeholder, will be calculated below
#                             "co2e_unit": emission.get("Unit"),
#                             "unit_type": emission.get("unit_type"),
#                             "unit1": "",
#                             "unit2": "",
#                             "activity_data": item,
#                         }
#                     )

#                     category_arr.append(
#                         {
#                             "scope_name": raw_response.path.split("-")[-1],
#                             "source_name": emission.get("Category"),
#                             "category_name": emission.get("Subcategory"),
#                             "activity_name": emission.get("Activity"),
#                             "total_co2e": round(quantity / 1000, 2),
#                             "contribution_source": 0,  # Placeholder, will be calculated below
#                             "co2e_unit": emission.get("Unit"),
#                             "unit_type": emission.get("unit_type"),
#                             "unit1": "",
#                             "unit2": "",
#                             "source": "",
#                             "activity_data": item,
#                         }
#                     )

#             if total_emission_value > 0:
#                 for scope in scope_arr:
#                     scope["contribution_scope"] = round(
#                         (scope["total_co2e"] * 1000 / total_emission_value) * 100, 2
#                     )

#                 for category in category_arr:
#                     category["contribution_source"] = round(
#                         (category["total_co2e"] * 1000 / total_emission_value) * 100, 2
#                     )

#             location_arr.append(
#                 {
#                     "corporate_name": corporate.name,
#                     "location_name": location.name,
#                     "location_address": f"{location.streetaddress}, {location.city}, {location.state} {location.zipcode}",
#                     "location_type": location.location_type,
#                     "total_co2e": round(total_emission_value / 1000, 2),
#                     "contribution_location": 100,  # Since it's the total for this location
#                 }
#             )

#         report_analysis_data = {
#             corporate.name: {
#                 "scope": scope_arr,
#                 "source": category_arr,
#                 "location": location_arr,
#                 "corporate": {
#                     "corporate_name": corporate.name,
#                     "scope": scope_arr,
#                     "source": category_arr,
#                     "location": location_arr,
#                 },
#             }
#         }

#         serialized_data = json.dumps(report_analysis_data, cls=DjangoJSONEncoder)

#         # Save the report_analysis_data dictionary in the AnalysisData JSONField
#         analysis_data_instance = AnalysisData2.objects.create(
#             report_id=report_id,
#             data=serialized_data,
#             client_id=client_id,
#         )

#         print(analysis_data_instance)
#         print(report_analysis_data)
#         return Response(
#             {
#                 "message": f"Calculation success, Report created successfully ID:{report_id}"
#             },
#             status=status.HTTP_200_OK,
#         )

#     except Exception as e:
#         print("Error:", e)
#         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_corporate_name(location_name):
    try:
        location = Location.objects.get(name=location_name)
        return location.corporateentity.name
    except Location.DoesNotExist:
        return "Unknown Corporate"


class ReportCreateView(generics.ListAPIView):
    serializer_class = GHGReportRawResponseSerializer
    permission_classes = [AllowAny]

    def get_emission_data(self, scope_name, corporate_id):
        try:
            loc_name = Location.objects.get(corporateentity=corporate_id).name
        except Location.DoesNotExist:
            loc_name = "Unknown Location"
        print(loc_name)
        raw_responses = RawResponse.objects.filter(
            path__name=scope_name,
            location=loc_name,
            year=2023,
            month=1,
        )

        corporate_data_dict = defaultdict(
            lambda: {
                "corporate_name": "",
                "scopes": defaultdict(
                    lambda: {
                        "scope_name": "",
                        "total_co2e": 0,
                        "contribution_scope": 0,
                        "co2e_unit": "kg",
                        "unit_type": "weight",
                        "unit1": "",
                        "unit2": "",
                        "activity_data": {"activity_unit": "", "activity_value": 0},
                        "emission_data": [],
                    }
                ),
                "locations": defaultdict(
                    lambda: {
                        "location_name": "",
                        "location_address": "",
                        "location_type": "",
                        "total_co2e": 0,
                        "contribution_scope": 0,
                    }
                ),
                "sources": defaultdict(list),
            }
        )

        for response in raw_responses:
            location_name = response.location
            corporate_name = get_corporate_name(location_name)
            scope_key = "-".join(scope_name.split("-")[-2:])

            corporate_data_dict[corporate_name]["corporate_name"] = corporate_name

            scope_data = corporate_data_dict[corporate_name]["scopes"][scope_key]
            scope_data["scope_name"] = scope_key

            location_data = self.process_location_data(
                corporate_data_dict, corporate_name, location_name
            )
            self.process_source_data(
                scope_data, location_data, response, corporate_data_dict, corporate_name
            )

        return corporate_data_dict

    def process_location_data(self, corporate_data_dict, corporate_name, location_name):
        location_data = corporate_data_dict[corporate_name]["locations"][location_name]
        location_data["location_name"] = location_name

        loc = Location.objects.get(name=location_name)
        street_address = loc.streetaddress
        city = loc.city
        state = loc.state
        zipcode = loc.zipcode
        location_data["location_address"] = (
            f"{street_address}, {city}, {state} {zipcode}"
        )
        location_data["location_type"] = loc.location_type

        return location_data

    def process_source_data(
        self, scope_data, location_data, response, corporate_data_dict, corporate_name
    ):
        for emission in response.data:
            unit = emission.get("Emission", {}).get("Unit", "")
            quantity = float(emission.get("Emission", {}).get("Quantity", 0) or 0)
            scope_data["unit1"] = unit
            scope_data["total_co2e"] += quantity
            scope_data["activity_data"]["activity_unit"] = unit
            scope_data["activity_data"]["activity_value"] += quantity
            location_data["total_co2e"] += quantity

            source_key = emission.get("Source", {}).get("Name", "")
            category_name = emission.get("Source", {}).get("Category", "")
            source_data = {
                "scope_name": scope_data["scope_name"],
                "source_name": source_key,
                "category_name": category_name,
                "activity_name": emission.get("Source", {}).get("Activity", ""),
                "total_co2e": quantity,
                "contribution_source": 0,  # Will be calculated later
                "co2e_unit": unit,
                "unit_type": emission.get("Emission", {}).get("Type", ""),
                "unit1": unit,
                "unit2": "",
                "source": emission.get("Source", {}).get("Source", ""),
                "activity_data": {
                    "activity_unit": unit,
                    "activity_value": quantity,
                },
            }
            corporate_data_dict[corporate_name]["sources"][
                scope_data["scope_name"]
            ].append(source_data)

    def calculate_total_all_scopes(self, corporate_data_dict):
        total = sum(
            scope["total_co2e"]
            for data in corporate_data_dict.values()
            for scope in data["scopes"].values()
        )
        return total

    def get_scope1_data(self):
        return self.get_emission_data("GRI-Collect-Emissions-Scope-1", corporate_id=1)

    def get_scope2_data(self):
        return self.get_emission_data("GRI-Collect-Emissions-Scope-2", corporate_id=1)

    def get_scope3_data(self):
        return self.get_emission_data("GRI-Collect-Emissions-Scope-3", corporate_id=1)

    def get_queryset(self):
        scope1_data = self.get_scope1_data()
        scope2_data = self.get_scope2_data()
        scope3_data = self.get_scope3_data()

        combined_data = defaultdict(
            lambda: {
                "corporate_name": "",
                "scopes": {},
                "locations": {},
                "sources": defaultdict(list),
            }
        )

        for data_dict in [scope1_data, scope2_data, scope3_data]:
            for corporate_name, data in data_dict.items():
                if corporate_name not in combined_data:
                    combined_data[corporate_name] = data
                else:
                    for scope_key, scope_value in data["scopes"].items():
                        if scope_key in combined_data[corporate_name]["scopes"]:
                            combined_data[corporate_name]["scopes"][scope_key][
                                "total_co2e"
                            ] += scope_value["total_co2e"]
                            combined_data[corporate_name]["scopes"][scope_key][
                                "activity_data"
                            ]["activity_value"] += scope_value["activity_data"][
                                "activity_value"
                            ]
                        else:
                            combined_data[corporate_name]["scopes"][
                                scope_key
                            ] = scope_value

                    for location_key, location_value in data["locations"].items():
                        if location_key in combined_data[corporate_name]["locations"]:
                            combined_data[corporate_name]["locations"][location_key][
                                "total_co2e"
                            ] += location_value["total_co2e"]
                        else:
                            combined_data[corporate_name]["locations"][
                                location_key
                            ] = location_value

                    for scope_key, sources_list in data["sources"].items():
                        combined_data[corporate_name]["sources"][scope_key].extend(
                            sources_list
                        )

        total_all_scopes = sum(
            scope["total_co2e"]
            for corporate_data in combined_data.values()
            for scope in corporate_data["scopes"].values()
        )

        corporate_data_list = []
        for corporate_name, data in combined_data.items():
            for scope in data["scopes"].values():
                if total_all_scopes > 0:
                    scope["contribution_scope"] = (
                        scope["total_co2e"] / total_all_scopes
                    ) * 100
                else:
                    scope["contribution_scope"] = 0

            for location in data["locations"].values():
                if total_all_scopes > 0:
                    location["contribution_scope"] = (
                        location["total_co2e"] / total_all_scopes
                    ) * 100
                else:
                    location["contribution_scope"] = 0

            for sources_list in data["sources"].values():
                for source in sources_list:
                    if total_all_scopes > 0:
                        source["contribution_source"] = (
                            source["total_co2e"] / total_all_scopes
                        ) * 100
                    else:
                        source["contribution_source"] = 0

            scopes = list(data["scopes"].values())
            locations = list(data["locations"].values())
            sources = [
                source
                for sources_list in data["sources"].values()
                for source in sources_list
            ]

            corporate_data_list.append(
                {
                    "corporate_name": corporate_name,
                    "scopes": scopes,
                    "locations": locations,
                    "sources": sources,
                }
            )

        print(corporate_data_list)
        print(f"Total CO2e for all corporates: {total_all_scopes}")
        # analysis_data_instance = AnalysisData2.objects.create(
        #     report_id=1, data=corporate_data_list, client_id=1
        # )

        return corporate_data_list
