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
from sustainapp.serializers import ReportSerializer, AnalysisDataResponseSerializer
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


class GHGReportView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        organization_id = self.request.data.get("organization")
        corporate_id = self.request.data.get("corporate")

        if organization_id:
            try:
                organization = Organization.objects.get(pk=organization_id)

                reports = (
                    organization.report_organization.all()
                )  # Use the correct related name here

                if corporate_id:
                    return reports.filter(corporate__id=corporate_id)
                else:
                    return reports

            except Organization.DoesNotExist:
                return Report.objects.none()
        else:
            return Report.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_report = serializer.save()
        report_id = new_report.id
        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")
        corporate_id = serializer.validated_data.get("corporate")
        organization = serializer.validated_data.get("organization")
        print("Corporate ID:", corporate_id)

        organization_id = organization.id
        print("Organization ID:", organization_id)
        start_month = start_date.month
        end_month = end_date.month
        start_year = start_date.year
        end_year = end_date.year
        print(start_month, end_month, start_year, end_year)
        if organization_id:
            corporate_ids = Corporateentity.objects.filter(
                organization_id=organization_id
            ).values_list("id", flat=True)
            corporate_ids_list = list(corporate_ids)
            print("Corporate IDs:", corporate_ids_list)
            # If a single corporate ID is provided, pass it to the function
            analysis_data = get_analysis_data(
                self,
                corporate_ids_list,
                start_year,
                end_year,
                start_month,
                end_month,
                report_id,
            )
        elif corporate_id:
            # If multiple corporate names are provided, pass the list of names
            analysis_data = get_analysis_data(
                self,
                corporate_id,
                start_year,
                end_year,
                start_month,
                end_month,
                report_id,
            )

        # if isinstance(analysis_data, Response):
        #     print("Analysis data is an instance of Response")
        #     status_check = analysis_data.status_code
        #     if status_check == 400:
        #         new_report.delete()
        #         print(analysis_data.status_code)
        #     return Response(
        #         {
        #             "id": serializer.data.get("id"),
        #             "start_date": serializer.data.get("start_date"),
        #             "end_date": serializer.data.get("end_date"),
        #             "country_name": serializer.data.get("organization_country"),
        #             "organization_name": serializer.data.get("organization_name"),
        #             "message": analysis_data.data["message"],
        #         },
        #         status=analysis_data.status_code,
        #     )
        print("Report created successfully")
        return Response(
            {"message": f"Report created successfully ID:{report_id}"},
            status=status.HTTP_200_OK,
        )


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


def get_analysis_data_by_location(self, data_points, locations):

    emission_by_location = defaultdict(
        lambda: {
            "corporate_name": "",
            "location_name": "",
            "location_address": "",
            "location_type": "",
            "total_co2e": 0,
            "contribution_scope": 0,
        }
    )
    total_co2e_all_locations = 0
    for loc in locations:
        corporate_name = loc.corporateentity.name
        location_name = loc.name
        location_type = loc.location_type
        location_address = f"{loc.streetaddress}, {loc.city}, {loc.state} {loc.zipcode}"
        emission_by_location[location_name]["location_name"] = location_name
        emission_by_location[location_name]["location_type"] = location_type
        emission_by_location[location_name]["location_address"] = location_address
        emission_by_location[location_name]["corporate_name"] = corporate_name

    for data in data_points:
        total_co2e = sum([i.get("co2e", 0) for i in data.json_holder])
        location_name = data.location
        emission_by_location[location_name]["total_co2e"] += total_co2e

        total_co2e_all_locations += total_co2e

    for location, emission_data in emission_by_location.items():
        if total_co2e_all_locations == 0:
            emission_by_location[location]["contribution_scope"] = 0
        else:
            emission_by_location[location]["contribution_scope"] = (
                emission_data["total_co2e"] / total_co2e_all_locations
            ) * 100

    # Transform the dictionary to a list and format the values
    result = [
        {
            "corporate_name": emission_data["corporate_name"],
            "location_name": emission_data["location_name"],
            "location_address": emission_data["location_address"],
            "location_type": emission_data["location_type"],
            "total_co2e": f"{emission_data['total_co2e']:.2f}",
            "contribution_scope": f"{emission_data['contribution_scope']:.2f}",
        }
        for emission_data in emission_by_location.values()
    ]

    return result


def get_analysis_data_by_source(self, data_points):
    # This will hold the final structured data
    grouped_data = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: {
                    "scope_name": "",
                    "source_name": "",
                    "category_name": "",
                    "activity_name": "",
                    "total_co2e": 0.0,
                    "contribution_source": 0.0,
                    "co2e_unit": "",
                    "unit_type": "",
                    "unit1": "",
                    "unit2": "",
                    "source": "",
                    "activity_data": [],
                }
            )
        )
    )
    total_co2e_all_sources = 0.0

    for data in data_points:
        path_name = data.raw_response.path.name
        scope_name = "-".join(path_name.split("-")[-2:])

        for emission_request, climatiq_response in zip(
            data.raw_response.data, data.json_holder
        ):
            category = emission_request["Emission"]["Category"]
            sub_category = emission_request["Emission"]["Subcategory"]
            activity = emission_request["Emission"]["Activity"]
            unit_type = emission_request["Emission"]["unit_type"]
            unit1 = emission_request["Emission"]["Unit"]
            # unit2 = emission_request["Emission"]["Unit2"] Need to find this too
            total_co2e = climatiq_response.get("co2e", 0)
            co2e_unit = climatiq_response.get("co2e_unit", "")
            activity_data = climatiq_response.get("activity_data", "")
            source = climatiq_response["emission_factor"]["source"]

            # Aggregate data by scope_name, category, and activity_name
            entry = grouped_data[scope_name][category][activity]
            entry["scope_name"] = scope_name
            entry["source_name"] = category
            entry["category_name"] = sub_category
            entry["activity_name"] = activity
            entry["unit1"] = unit1
            # entry["unit2"] = unit2
            entry["unit_type"] = unit_type
            entry["source"] = source
            entry["activity_data"] = activity_data
            entry["co2e_unit"] = co2e_unit
            entry["total_co2e"] += total_co2e

            total_co2e_all_sources += total_co2e

    for scope_dict in grouped_data.values():
        for category_dict in scope_dict.values():
            for entry in category_dict.values():
                if total_co2e_all_sources > 0:
                    entry["contribution_source"] = (
                        entry["total_co2e"] / total_co2e_all_sources
                    ) * 100

    # Flatten the nested dictionary into a list of dictionaries
    structured_data = [
        entry
        for scope_dict in grouped_data.values()
        for category_dict in scope_dict.values()
        for entry in category_dict.values()
    ]

    # for entry in structured_data:
    #     print(entry)

    return structured_data


def get_analysis_data(
    self, corporate_id, start_year, end_year, start_month, end_month, report_id
):
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
    analysis_data_by_corporate = defaultdict(dict)
    print(corporate_id)
    for id in corporate_id:
        locations = Location.objects.filter(corporateentity=id)
        location_names = locations.values_list("name", flat=True)
        corporate_name = Corporateentity.objects.get(pk=id).name
        print(location_names)
        # * Get all Raw Respones based on location and year.
        raw_responses = RawResponse.objects.filter(
            path__slug__icontains="gri-environment-emissions-301-a-scope-",
            year__range=(start_year, end_year),
            month__range=(start_month, end_month),
            location__in=location_names,
        )

        data_points = DataPoint.objects.filter(
            raw_response__in=raw_responses, json_holder__isnull=False
        ).select_related("raw_response")

        emission_by_source = get_analysis_data_by_source(self, data_points)

        emission_by_location = get_analysis_data_by_location(
            self, data_points, locations
        )

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
            for r in data.raw_response.data:
                unit1 = r["Emission"]["Unit"]
                unit_type = r["Emission"]["unit_type"]

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
            emission_by_scope[scope_name]["unit1"] = unit1
            emission_by_scope[scope_name]["unit_type"] = unit_type
            emission_by_scope[scope_name]["activity_data"][
                "activity_unit"
            ] = activity_unit
            emission_by_scope[scope_name]["activity_data"][
                "activity_value"
            ] += activity_value
            emission_by_scope[scope_name]["entries"].extend(data.json_holder)

        # Example total emissions for calculating contributions
        total_emissions = sum([v["total_co2e"] for v in emission_by_scope.values()])

        data = calculate_contributions(self, emission_by_scope, total_emissions)

        analysis_data_by_corporate[corporate_name] = {
            "scopes": calculate_contributions(self, emission_by_scope, total_emissions),
            "locations": emission_by_location,
            "sources": emission_by_source,
        }
        restructured_data = {}

        for corporate_name, corporate_data in analysis_data_by_corporate.items():
            corporate_entry = {
                "corporate_name": corporate_name,
                "scope": corporate_data["scopes"],
                "location": corporate_data["locations"],
                "source": corporate_data["sources"],
            }

            restructured_data[corporate_name] = corporate_entry

    serialized_data = json.dumps(restructured_data, cls=DjangoJSONEncoder)
    # Save the report_analysis_data dictionary in the AnalysisData JSONField
    analysis_data_instance = AnalysisData2.objects.create(
        report_id=report_id,
        data=serialized_data,
        client_id=1,
    )
    # Print the structured list of dictionaries
    return restructured_data


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
        report_id = request.GET.get("report_id")
        print(organization_id)

        if organization_id:
            corporate_ids = Corporateentity.objects.filter(
                organization_id=organization_id
            ).values_list("id", flat=True)
            corporate_ids_list = list(corporate_ids)
            print("Corporate IDs:", corporate_ids_list)
            data = get_analysis_data(
                self,
                corporate_ids_list,
                start_year,
                end_year,
                start_month,
                end_month,
                report_id,
            )
        else:
            data = get_analysis_data(
                self,
                corporate_id,
                start_year,
                end_year,
                start_month,
                end_month,
                report_id,
            )

        return Response(
            (data),
            status=status.HTTP_200_OK,
        )


class AnalysisData2APIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, report_id):
        try:
            instance = AnalysisData2.objects.get(report_id=report_id)
            data_dict = json.loads(instance.data)

            organized_data_list = []

            # Iterate over each corporate in data_dict
            for corporate_name, corporate_data in data_dict.items():
                corporate_name = corporate_data.get("corporate_name", [])
                scopes = corporate_data.get("scope", [])
                locations = corporate_data.get("location", [])
                sources = corporate_data.get("source", [])

                # Organize the data into the desired structure
                organized_data = {
                    "corporate_name": corporate_name,
                    "scopes": scopes,
                    "locations": locations,
                    "sources": sources,
                }

                organized_data_list.append(organized_data)
                print(organized_data)

            # Use the serializer to validate and deserialize the data
            serializer = AnalysisDataResponseSerializer(
                data={"data": organized_data_list}
            )
            serializer.is_valid(
                raise_exception=True
            )  # Ensure to raise an exception for invalid data
            deserialized_data = serializer.validated_data
            print(deserialized_data)
            return Response(deserialized_data, status=status.HTTP_200_OK)

        except AnalysisData2.DoesNotExist:
            return Response(
                {"error": f"Data not found for ID {report_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
