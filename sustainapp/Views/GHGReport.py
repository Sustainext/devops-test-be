import json
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import (
    Corporateentity,
    AnalysisData2,
    Report,
    Location,
    Organization,
)
from rest_framework import viewsets, generics
from sustainapp.serializers import ReportSerializer
from rest_framework.permissions import AllowAny
from datametric.models import RawResponse, DataPoint
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


def calculate_contributions(self, emission_by_scope, total_emissions):
    """
    Calculates the contribution of each scope to the total emissions.

    Args:
        emission_by_scope (dict): A dictionary where the keys are scope names and the values are dictionaries containing the scope details.
        total_emissions (float): The total emissions across all scopes.

    """
    # Convert defaultdict to a list of dictionaries with the required structure
    structured_emission_data = []
    for scope, values in emission_by_scope.items():
        contribution_scope = (
            (values["total_co2e"] / total_emissions) * 100 if total_emissions else 0
        )
        structured_emission_data.append(
            {
                "scope_name": values["scope_name"],
                "total_co2e": values["total_co2e"],
                "contribution_scope": contribution_scope,
                "co2e_unit": values["co2e_unit"],
                "unit_type": values["unit_type"],
                "unit1": values["unit1"],
                "unit2": "",  # Add logic to determine unit2 if needed
                "activity_data": values["activity_data"],
            }
        )
    return structured_emission_data


def get_analysis_data(self, corporate_id, start_year, end_year, start_month, end_month):
    """
    Retrieves analysis data for a given set of corporate IDs, start and end years, and start and end months.

    Args:
        self (ReportDetails): The ReportDetails instance.
        corporate_id (list): A list of corporate IDs.
        start_year (str): The start year for the analysis.
        end_year (str): The end year for the analysis.
        start_month (str): The start month for the analysis.
        end_month (str): The end month for the analysis.

    Returns:
        dict: A dictionary containing the analysis data, including the contribution of each scope to the total emissions.

    Task left to do:
        * Add logic to determine unit1, take it from rawresponse>data>emission>unit.
        * Need to Find unit2.
        * Add logic to determine unit_type, take it from rawresponse>data>emission>unit_type .
        * Still need to work on Scource data and location data
        * Refactor and optimization
    """

    location = Location.objects.filter(id__in=corporate_id)
    print(location)
    # * Get all Raw Respones based on location and year.
    raw_responses = RawResponse.objects.filter(
        path__slug__icontains="gri-environment-emissions-301-a-scope-",
        year__range=(start_year, end_year),
        month__range=(start_month, end_month),
    ).all()

    data_points = DataPoint.objects.filter(
        raw_response__in=raw_responses, json_holder__isnull=False
    ).select_related("raw_response")

    emission_by_source = defaultdict(lambda: 0)
    emission_by_location = defaultdict(lambda: 0)

    emission_by_scope = defaultdict(
        lambda: {
            "scope_name": "",
            "total_co2e": 0,
            "co2e_unit": "",
            "unit_type": "",  # Need to Find this
            "unit1": "",
            "unit2": "",
            "activity_data": {"activity_unit": "", "activity_value": 0},
            "entries": [],
        }
    )

    # Assuming data_points is a list of objects containing the necessary data
    for data in data_points:
        path_name = data.raw_response.path.name
        scope_name = "-".join(path_name.split("-")[-2:])

        # Summing up the CO2e values
        total_co2e = sum([i.get("co2e", 0) for i in data.json_holder])
        co2e_unit = ""
        activity_unit = ""
        activity_value = 0
        activity_data = {}

        # Assuming all entries have the same unit and activity data
        if data.json_holder:
            first_entry = data.json_holder[0]
            co2e_unit = first_entry.get("co2e_unit", "")
            activity_data = first_entry.get("activity_data", {})
            activity_unit = activity_data.get("activity_unit", "")
            activity_value = sum(
                [
                    i.get("activity_data", {}).get("activity_value", 0)
                    for i in data.json_holder
                ]
            )

        # Update the defaultdict with the new values
        emission_by_scope[scope_name]["scope_name"] = scope_name
        emission_by_scope[scope_name]["total_co2e"] += total_co2e
        emission_by_scope[scope_name]["co2e_unit"] = co2e_unit
        emission_by_scope[scope_name]["activity_data"]["activity_unit"] = activity_unit
        emission_by_scope[scope_name]["activity_data"][
            "activity_value"
        ] += activity_value
        emission_by_scope[scope_name]["unit1"] = data.value[0]
        emission_by_scope[scope_name]["entries"].extend(data.json_holder)

    # Example total emissions for calculating contributions
    total_emissions = sum([v["total_co2e"] for v in emission_by_scope.values()])

    data = calculate_contributions(self, emission_by_scope, total_emissions)

    # Print the structured list of dictionaries
    print({"scopes": data})
    return data


class ReportDetails(APIView):
    """
    Class to retrieve the analysis data for a given set of corporate IDs, start and end years, and start and end months.

    Task Left to do:
        * Add proper way to retrive data( not params, get from POST)
        * Add handling when corporate_id is send
        * Need to change view from APIView to ModelViewSet
        * Remove AllowAny permission class
    """

    permission_classes = [AllowAny]

    def get(self, request):
        corporate_id = request.GET.get("corporate_id")
        start_year = request.GET.get("start_year")
        end_year = request.GET.get("end_year")
        start_month = request.GET.get("start_month")
        end_month = request.GET.get("end_month")
        organization_id = request.GET.get("organization_id")
        print(organization_id)

        if organization_id:
            corporate_ids = Corporateentity.objects.filter(
                organization_id=organization_id
            ).values_list("id", flat=True)
            corporate_ids_list = list(corporate_ids)
            print("Corporate IDs:", corporate_ids_list)
            data = get_analysis_data(
                self, corporate_ids_list, start_year, end_year, start_month, end_month
            )

        return Response(
            (data),
            status=status.HTTP_200_OK,
        )
