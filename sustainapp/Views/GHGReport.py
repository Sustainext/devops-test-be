import json
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
from django.views.generic import View
from sustainapp.serializers import (
    ReportSerializer,
    AnalysisDataResponseSerializer,
    ReportUpdateSerializer,
    ReportRetrieveSerializer,
)
from rest_framework.permissions import AllowAny
from datametric.models import RawResponse, DataPoint
from rest_framework.views import APIView
from collections import defaultdict
from django.conf import settings
import os
from django.core.files.base import ContentFile
import logging
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import time
from sustainapp.report import generate_pdf_data
from django.core.files.storage import default_storage
from datametric.utils.analyse import filter_by_start_end_dates
from esg_report.utils import create_validation_method_for_report_creation

logger = logging.getLogger()


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
                "contribution_scope": round(contribution_scope, 2),
                "co2e_unit": values["co2e_unit"],
                "unit_type": values["unit_type"],
                "unit1": values["unit1"],
                "unit2": values["unit2"],  # Add logic to determine unit2 if needed
                "activity_data": values["activity_data"],
            }
        )
    return structured_emission_data


def get_analysis_data_by_location(self, data_points, locations):
    """
    Retrieves the emission data by location and calculates the total emissions and contribution of each location to the overall emissions.

    Args:
        data_points (list): A list of data points containing emission data.
        locations (list): A list of locations associated with the emission data.

    Returns:
        list: A list of dictionaries containing the emission data for each location, including the corporate name, location name, location address, location type, total CO2e, and contribution to the overall emissions.

    Removed:
        *It dosen't saves those locations where there is no emission data.
    """
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

    # Initialize emission data for all locations
    for loc in locations:
        corporate_name = loc.corporateentity.name
        location_name = loc.name
        location_type = loc.location_type
        location_address = f"{loc.streetaddress}, {loc.city}, {loc.state} {loc.zipcode}"
        emission_by_location[location_name]["location_name"] = location_name
        emission_by_location[location_name]["location_type"] = location_type
        emission_by_location[location_name]["location_address"] = location_address
        emission_by_location[location_name]["corporate_name"] = corporate_name

    # Update emission data based on data points
    for data in data_points:
        total_co2e = sum([i.get("co2e", 0) for i in data.json_holder])
        location_name = data.locale.name  # Assuming location name is available here
        if location_name in emission_by_location:
            emission_by_location[location_name]["total_co2e"] += total_co2e
            total_co2e_all_locations += total_co2e

    # Calculate contribution scope for each location
    for location, emission_data in emission_by_location.items():
        if emission_data["total_co2e"] == 0:
            # Skip locations without emissions
            continue
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
            "total_co2e": round(emission_data["total_co2e"], 2),
            "contribution_scope": round(emission_data["contribution_scope"], 2),
        }
        for emission_data in emission_by_location.values()
        if emission_data["total_co2e"] > 0
    ]

    return result


def get_analysis_data_by_source(self, data_points):
    """Function to gather source data inside data points and then make it on proper structure

    Args:
        data_points (list): A list of data points.

    Finds the source name, category name, activity name and total emissions for each source.

    Value to Find
    * Need to find from where Unit2 will come.

    """
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
                    "unit2": "",  # TODO: Need to find this
                    "source": "",
                    "year": "",
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
            unit2 = (
                emission_request["Emission"]["Unit2"]
                if "Unit2" in emission_request["Emission"]
                else ""
            )  # Need to find this too
            total_co2e = climatiq_response.get("co2e", 0)
            total_co2e = total_co2e / 1000  # Convert to tonnes
            co2e_unit = climatiq_response.get("co2e_unit", "")
            activity_data = climatiq_response.get("activity_data", "")
            source = climatiq_response["emission_factor"]["source"]
            year = climatiq_response["emission_factor"]["year"]

            # Aggregate data by scope_name, category, and activity_name
            entry = grouped_data[scope_name][category][activity]
            entry["scope_name"] = scope_name
            entry["source_name"] = category
            entry["category_name"] = sub_category
            entry["activity_name"] = activity
            entry["unit1"] = unit1
            entry["unit2"] = unit2
            entry["unit_type"] = unit_type
            entry["source"] = source
            entry["activity_data"] = activity_data
            entry["co2e_unit"] = co2e_unit
            entry["total_co2e"] += round(total_co2e, 2)
            entry["year"] = year

            total_co2e_all_sources += total_co2e

    for scope_dict in grouped_data.values():
        for category_dict in scope_dict.values():
            for entry in category_dict.values():
                if total_co2e_all_sources > 0:
                    entry["contribution_source"] = round(
                        (entry["total_co2e"] / total_co2e_all_sources) * 100, 2
                    )

    # Flatten the nested dictionary into a list of dictionaries
    structured_data = [
        entry
        for scope_dict in grouped_data.values()
        for category_dict in scope_dict.values()
        for entry in category_dict.values()
    ]

    return structured_data


def get_analysis_data(
    self,
    corporate_id,
    start_date,
    end_date,
    report_id,
    client_id,
    report_by,
    report_type,
    investment_corporates=None,  # Added argument for investment corporates
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
        investment_corporates (list): A list of investment corporate IDs.

    Returns:
        dict: A dictionary containing the analysis data, including the contribution of each scope to the total emissions.
    """
    analysis_data_by_corporate = defaultdict(dict)

    # Process regular corporates
    if isinstance(corporate_id, list) and report_by == "Organization":
        # If corporate_id is a list with more than one element, iterate over it
        for id in corporate_id:
            process_corporate_data(
                self,
                id,
                start_date,
                end_date,
                client_id,
                "Regular",
                analysis_data_by_corporate,
            )
    else:
        # If corporate_id is a single element, process it
        process_corporate_data(
            self,
            corporate_id.id,
            start_date,
            end_date,
            client_id,
            "Regular",
            analysis_data_by_corporate,
        )

    # Process investment corporates if provided
    if investment_corporates and report_type == "GHG Report - Investments":
        for investment_corporate in investment_corporates:
            id = investment_corporate["corporate_id"]
            ownership_ratio = investment_corporate["ownership_ratio"]
            process_corporate_data(
                self,
                id,
                start_date,
                end_date,
                client_id,
                "Investment",
                analysis_data_by_corporate,
                ownership_ratio,
            )
    # * Added Condition such that if there is no data for the corporate for GHG report, it will not throw an error for ESG Report.
    if (
        not analysis_data_by_corporate
        and report_type != "GRI Report: In accordance With"
    ):
        return Response(
            {"message": "No data available for the given corporate IDs."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Restructure data for the final response
    restructured_data = {}

    for corporate_name, corporate_data in analysis_data_by_corporate.items():
        corporate_entry = {
            "corporate_name": corporate_name,
            "corporate_type": corporate_data[
                "corporate_type"
            ],  # Include corporate_type
            "scope": corporate_data["scopes"],
            "location": corporate_data["locations"],
            "source": corporate_data["sources"],
        }

        restructured_data[corporate_name] = corporate_entry

    try:
        serialized_data = json.dumps(restructured_data, cls=DjangoJSONEncoder)
    except UnboundLocalError as e:
        logger.error(f"Error in GHGReportView: {e}")
        return Response(
            {"message": "No data available for the given corporate IDs."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Save the report_analysis_data dictionary in the AnalysisData JSONField
    analysis_data_instance = AnalysisData2.objects.create(
        report_id=report_id,
        data=serialized_data,
        client_id=client_id,
    )
    analysis_data_instance.save()

    return Response(
        {"message": f"Calculation success, Report created successfully ID:{report_id}"},
        status=status.HTTP_200_OK,
    )


def process_corporate_data(
    self,
    id,
    start_date,
    end_date,
    client_id,
    corporate_type,
    analysis_data_by_corporate,
    ownership_ratio=None,
):
    locations = Location.objects.filter(corporateentity=id)
    location_names = locations.values_list("id", flat=True)
    corporate_name = Corporateentity.objects.get(pk=id).name

    co2e_unit = ""
    activity_unit = ""
    activity_value = 0
    activity_data = {}

    # Get all Raw Responses based on location and year.
    raw_responses = RawResponse.objects.filter(
        path__slug__icontains="gri-environment-emissions-301-a-scope-",
        locale__in=location_names,
        client_id=client_id,
    ).filter(filter_by_start_end_dates(start_date=start_date, end_date=end_date))

    data_points = DataPoint.objects.filter(
        raw_response__in=raw_responses, json_holder__isnull=False
    ).select_related("raw_response")

    if not data_points:
        return

    if corporate_type == "Investment":
        emission_by_scope = defaultdict(
            lambda: {
                "scope_name": "Scope-3",  # Aggregate under Scope-3
                "total_co2e": 0,
                "co2e_unit": "",
                "unit_type": "",
                "unit1": "",
                "unit2": "",
                "activity_data": {"activity_unit": "", "activity_value": 0},
                "entries": [],
            }
        )
        emission_by_source = defaultdict(
            lambda: {
                "scope_name": "Scope-3",
                "source_name": corporate_name,
                "category_name": "Investment",
                "activity_name": "On other Corporates",
                "source": "Other",
                "year": 2024,
                "total_co2e": 0,
                "contribution_source": 0,
                "activity_data": {
                    "activity_unit": "-",
                },
            }
        )
        total_co2e = 0
        for data in data_points:
            # Sum up the CO2e from all scopes
            scope_co2e = sum([i.get("co2e", 0) for i in data.json_holder])
            if ownership_ratio:
                scope_co2e = (scope_co2e * ownership_ratio) / 100
            scope_co2e = scope_co2e / 1000 if scope_co2e > 0 else 0
            total_co2e += scope_co2e

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

            # Aggregate everything under Scope-3
            emission_by_scope["Scope-3"]["total_co2e"] += scope_co2e
            emission_by_scope["Scope-3"]["co2e_unit"] = co2e_unit
            emission_by_scope["Scope-3"]["activity_data"][
                "activity_unit"
            ] = activity_unit
            emission_by_scope["Scope-3"]["activity_data"][
                "activity_value"
            ] += activity_value

            # Aggregate the CO2e values by source
            emission_by_source["investment_source"]["total_co2e"] += scope_co2e

        structured_emission_data = calculate_contributions(
            self, emission_by_scope, total_co2e
        )

        # Calculate contribution for the source
        for source, values in emission_by_source.items():
            contribution_source = (
                (values["total_co2e"] / total_co2e) * 100 if total_co2e else 0
            )
            emission_by_source[source]["contribution"] = round(contribution_source, 2)

        analysis_data_by_corporate[corporate_name] = {
            "corporate_type": corporate_type,
            "scopes": structured_emission_data,  # Convert defaultdict to regular dict
            "locations": [],
            "sources": list(emission_by_source.values()),
        }
    else:
        # Regular corporate processing (as you have already implemented)
        emission_by_source = get_analysis_data_by_source(self, data_points)
        emission_by_location = get_analysis_data_by_location(
            self, data_points, locations
        )
        emission_by_scope = defaultdict(
            lambda: {
                "scope_name": "",
                "total_co2e": 0,
                "co2e_unit": "",
                "unit_type": "",
                "unit1": "",
                "unit2": "",
                "activity_data": {"activity_unit": "", "activity_value": 0},
                "entries": [],
            }
        )

        for data in data_points:
            path_name = data.raw_response.path.name
            scope_name = "-".join(path_name.split("-")[-2:])
            for r in data.raw_response.data:
                unit1 = r["Emission"]["Unit"] if "Unit" in r["Emission"] else ""
                unit2 = r["Emission"]["Unit2"] if "Unit2" in r["Emission"] else ""
                unit_type = (
                    r["Emission"]["unit_type"] if "unit_type" in r["Emission"] else ""
                )

            total_co2e = sum([i.get("co2e", 0) for i in data.json_holder])
            total_co2e = total_co2e / 1000 if total_co2e > 0 else 0

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

            emission_by_scope[scope_name]["scope_name"] = scope_name
            emission_by_scope[scope_name]["total_co2e"] += round(total_co2e, 2)
            emission_by_scope[scope_name]["co2e_unit"] = co2e_unit
            try:
                emission_by_scope[scope_name]["unit1"] = unit1
                emission_by_scope[scope_name]["unit2"] = unit2
                emission_by_scope[scope_name]["unit_type"] = unit_type
            except UnboundLocalError as e:
                emission_by_scope[scope_name]["unit1"] = ""
                emission_by_scope[scope_name]["unit2"] = ""
                emission_by_scope[scope_name]["unit_type"] = ""

            emission_by_scope[scope_name]["activity_data"][
                "activity_unit"
            ] = activity_unit
            emission_by_scope[scope_name]["activity_data"][
                "activity_value"
            ] += activity_value
            emission_by_scope[scope_name]["entries"].extend(data.json_holder)

        total_emissions = sum([v["total_co2e"] for v in emission_by_scope.values()])
        scopes = calculate_contributions(self, emission_by_scope, total_emissions)

        analysis_data_by_corporate[corporate_name] = {
            "corporate_type": corporate_type,  # Add corporate_type here
            "scopes": scopes,
            "locations": emission_by_location,
            "sources": emission_by_source,
        }


class GHGReportView(generics.CreateAPIView):
    serializer_class = ReportSerializer

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

        status = 1
        client_id = request.user.client.id
        user_id = request.user.id

        new_report = serializer.save(
            status=status, client_id=client_id, user_id=user_id
        )
        create_validation_method_for_report_creation(report=new_report)
        report_id = new_report.id
        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")
        corporate_id = serializer.validated_data.get("corporate")
        organization = serializer.validated_data.get("organization")
        report_by = serializer.validated_data.get("report_by")
        report_type = serializer.validated_data.get("report_type")
        investment_corporates = serializer.validated_data.get("investment_corporates")
        organization_id = organization.id

        print(report_by)

        if corporate_id and organization_id:
            # If multiple corporate names are provided, pass the list of names
            analysis_data = get_analysis_data(
                self,
                corporate_id,
                start_date,
                end_date,
                report_id,
                client_id,
                report_by,
                report_type,
                investment_corporates,
            )

        elif organization_id and corporate_id == None:
            corporate_ids = Corporateentity.objects.filter(
                organization_id=organization_id
            ).values_list("id", flat=True)
            corporate_ids_list = list(corporate_ids)
            # If a single corporate ID is provided, pass it to the function
            analysis_data = get_analysis_data(
                self,
                corporate_ids_list,
                start_date,
                end_date,
                report_id,
                client_id,
                report_by,
                report_type,
                investment_corporates,
            )

        if report_by == "Organization":
            common_name = organization.name
        else:
            common_name = corporate_id.name

        if isinstance(analysis_data, Response):
            status_check = analysis_data.status_code
            if status_check in [204, 404, 400, 500]:
                new_report.delete()
            return Response(
                {
                    "id": serializer.data.get("id"),
                    "start_date": serializer.data.get("start_date"),
                    "end_date": serializer.data.get("end_date"),
                    "country_name": serializer.data.get("organization_country"),
                    "organization_name": common_name,
                    "report_by": report_by,
                    "message": analysis_data.data["message"],
                    "report_type": serializer.validated_data["report_type"],
                },
                status=analysis_data.status_code,
            )
        return Response(
            {"message": f"Report created successfully ID:{report_id}"},
            status=status.HTTP_200_OK,
        )


class AnalysisData2APIView(APIView):

    def get(self, request, report_id):
        try:
            instance = AnalysisData2.objects.get(report_id=report_id)
            data_dict = json.loads(instance.data)

            organized_data_list = []

            # Iterate over each corporate in data_dict
            for corporate_name, corporate_data in data_dict.items():
                corporate_name = corporate_data.get("corporate_name", [])
                corporate_type = corporate_data.get("corporate_type", [])
                scopes = corporate_data.get("scope", [])
                locations = corporate_data.get("location", [])
                sources = corporate_data.get("source", [])

                # Organize the data into the desired structure
                organized_data = {
                    "corporate_name": corporate_name,
                    "corporate_type": corporate_type,
                    "scopes": scopes,
                    "locations": locations,
                    "sources": sources,
                }

                organized_data_list.append(organized_data)

            # Use the serializer to validate and deserialize the data
            serializer = AnalysisDataResponseSerializer(
                data={"data": organized_data_list}
            )
            serializer.is_valid(
                raise_exception=True
            )  # Ensure to raise an exception for invalid data
            deserialized_data = serializer.validated_data
            return Response(deserialized_data, status=status.HTTP_200_OK)

        except AnalysisData2.DoesNotExist:
            return Response(
                {"error": f"Data not found for ID {report_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ReportListView(generics.ListAPIView):
    serializer_class = ReportRetrieveSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        if not user_id:
            # Returning an empty queryset if user_id is not provided
            return Report.objects.none()

        try:
            user_id = int(user_id)
        except ValueError:
            return Report.objects.none()

        queryset = Report.objects.filter(user=user_id, status=1)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"message": "No reports found for the given user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()

            # Your custom logic here
            reset_logo = (
                "org_logo" in request.data and request.data.get("org_logo") == "null"
            )
            org_logo = request.FILES.get("org_logo", None)

            if reset_logo:
                default_image_path = default_storage.path("sustainext.jpeg")
                with default_storage.open(default_image_path, "rb") as image_file:
                    # Read the image content and save it to the instance's logo field
                    instance.org_logo.save(
                        os.path.basename(default_image_path),
                        ContentFile(image_file.read()),
                        save=True,
                    )
            elif org_logo is not None:
                instance.org_logo = org_logo

            data_field = request.data.get("data")
            if data_field:
                try:
                    data = json.loads(data_field)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid JSON format."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                data = request.data

            serializer = self.get_serializer(instance, data=data, partial=partial)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch any unexpected exceptions during report update
            return Response(
                {"error": {"message": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def perform_update(self, serializer):
        serializer.save()


class ReportPDFView(View):
    def get(self, request, *args, **kwargs):
        start_time = time.time()

        pk = self.kwargs.get("pk")
        try:
            report = get_object_or_404(Report, pk=pk)
        except:
            return HttpResponse("No report with ID={0}".format(pk), status=404)

        context = generate_pdf_data(pk)  # Function is defined in reports.py
        if context is None:
            return JsonResponse({"error": "Failed to generate PDF data"}, status=500)

        template_path = "sustainapp/pdf.html"
        template = get_template(template_path)
        html = template.render(context, request)
        response = HttpResponse(content_type="application/pdf")

        try:
            disposition = "attachment" if "download" in request.GET else "inline"
            pdf_filename = f"{context['object_list'].name}.pdf"
            response["Content-Disposition"] = (
                f'{disposition}; filename="{pdf_filename}"'
            )

            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse("Error generating PDF", status=500)

            print(
                f"Total time taken to generate PDF is {time.time() - start_time} seconds."
            )
            return response

        except Exception as e:
            # Log the exception and prepare an error response
            logger.exception("Unexpected error generating PDF")
            return HttpResponse("Unexpected error occurred", status=500)
