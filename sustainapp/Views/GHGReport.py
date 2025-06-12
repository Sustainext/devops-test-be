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
    ReportRetrieveSerializer,
)
from datametric.models import RawResponse, DataPoint
from rest_framework.views import APIView
from collections import defaultdict
from django.conf import settings
from django.core.files.base import ContentFile
import logging
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import time
from sustainapp.report import generate_pdf_data
from datametric.utils.analyse import filter_by_start_end_dates
from esg_report.utils import create_validation_method_for_report_creation
from azure.storage.blob import BlobClient
from datetime import datetime
from esg_report.models.ReportAssessment import ReportAssessment
from apps.canada_bill_s211.v2.utils.check_status_report import (
    is_canada_bill_s211_v2_completed,
)
from common.utils.value_types import format_decimal_places
from esg_report.Utils.CustomReportValidator import CustomEsgReportValidator

logger = logging.getLogger()


def format_created_at(created_at):
    """Format the created_at field into '19 Nov 2024 10:40:45 am'."""
    if created_at:
        dt_object = datetime.fromisoformat(created_at)
        return dt_object.strftime("%d %b %Y %I:%M:%S %p").lower()
    return None


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
                "total_co2e": round(values["total_co2e"], 2),
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
            "total_co2e": round(emission_data["total_co2e"] / 1000, 2),
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
            total_co2e = round(climatiq_response.get("co2e", 0), 2)
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
                entry["total_co2e"] = round(entry["total_co2e"], 2)
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


def process_emission_by_scope(data_points, ownership_ratio=None):
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

    total_co2e = 0

    for data in data_points:
        path_name = data.raw_response.path.name
        scope_name = "-".join(path_name.split("-")[-2:])
        for r in data.raw_response.data:
            unit1 = r["Emission"].get("Unit", "")
            unit2 = r["Emission"].get("Unit2", "")
            unit_type = r["Emission"].get("unit_type", "")

        co2e_sum = sum([i.get("co2e", 0) for i in data.json_holder])
        if ownership_ratio:
            co2e_sum = (co2e_sum * ownership_ratio) / 100
        co2e_sum = co2e_sum / 1000 if co2e_sum > 0 else 0
        total_co2e += co2e_sum

        co2e_unit = ""
        activity_unit = ""
        activity_value = 0
        activity_data = {}
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

        scope_data = emission_by_scope[scope_name]
        scope_data["scope_name"] = scope_name
        scope_data["total_co2e"] += co2e_sum
        scope_data["co2e_unit"] = co2e_unit
        scope_data["unit1"] = unit1
        scope_data["unit2"] = unit2
        scope_data["unit_type"] = unit_type
        scope_data["activity_data"]["activity_unit"] = activity_unit
        scope_data["activity_data"]["activity_value"] += activity_value
        scope_data["entries"].extend(data.json_holder)

    for data in emission_by_scope.values():
        data["total_co2e"] = float(format_decimal_places(data["total_co2e"]))

    return emission_by_scope, total_co2e


def calculate_contributions_for_source(processed_data):
    """
    Calculates the contribution of each scource to the total emissions.

    Args:
        processed_data (dict): A dictionary where the keys are corporate names and the values are dictionaries containing scope data.

    Returns:
        None: The function modifies the input dictionary in place.
    """
    total_emissions = 0
    for corporate_name, corporate_data in processed_data.items():
        for source in corporate_data["sources"]:
            total_emissions += source["total_co2e"]

    for corporate_name, corporate_data in processed_data.items():
        for source in corporate_data["sources"]:
            if total_emissions > 0:
                contribution_source = (source["total_co2e"] / total_emissions) * 100
            else:
                contribution_source = 0
            source["contribution_source"] = float(
                format_decimal_places(contribution_source)
            )


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
    if report_type in ["GHG Report - Investments", "GHG Accounting Report"]:
        # The contrubution_source to be calculated based on the total emissions of all corporates
        calculate_contributions_for_source(analysis_data_by_corporate)

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

        if corporate_data.get("ownership_ratio", None):
            corporate_entry["ownership_ratio"] = corporate_data["ownership_ratio"]

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
    if corporate_type == "Investment":
        raw_responses = RawResponse.objects.filter(
            path__slug__in=[
                "gri-environment-emissions-301-a-scope-1",
                "gri-environment-emissions-301-a-scope-2",
            ],
            locale__in=location_names,
            client_id=client_id,
        ).filter(filter_by_start_end_dates(start_date=start_date, end_date=end_date))
    else:
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
        emission_by_scope, _ = process_emission_by_scope(data_points, ownership_ratio)
        emission_by_source = defaultdict(
            lambda: {
                "scope_name": "Scope-3",
                "source_name": corporate_name,
                "category_name": "Investments",
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
        emission_by_scope["Scope-3"]["scope_name"] = "Scope-3"
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

            emission_by_scope["Scope-3"]["total_co2e"] += float(
                format_decimal_places(scope_co2e)
            )
            emission_by_scope["Scope-3"]["co2e_unit"] = co2e_unit
            emission_by_scope["Scope-3"]["activity_data"]["activity_unit"] = (
                activity_unit
            )
            emission_by_scope["Scope-3"]["activity_data"]["activity_value"] += (
                activity_value
            )
            emission_by_scope["Scope-3"]["year"] = "-"

            # Aggregate the CO2e values by source
            emission_by_source["investment_source"]["total_co2e"] += scope_co2e
        structured_emission_data = calculate_contributions(
            self, emission_by_scope, total_co2e
        )

        # Calculate contribution for the source
        for source, values in emission_by_source.items():
            emission_by_source[source]["total_co2e"] = float(
                format_decimal_places(emission_by_source[source]["total_co2e"])
            )
            contribution = (
                (values["total_co2e"] / total_co2e) * 100 if total_co2e else 0
            )
            emission_by_source[source]["contribution"] = float(
                format_decimal_places(contribution)
            )

        analysis_data_by_corporate[corporate_name] = {
            "corporate_type": corporate_type,
            "scopes": structured_emission_data,  # Convert defaultdict to regular dict
            "locations": [],
            "sources": list(emission_by_source.values()),
            "ownership_ratio": ownership_ratio if ownership_ratio else None,
        }
    else:
        # Regular corporate processing (as you have already implemented)
        emission_by_source = get_analysis_data_by_source(self, data_points)
        emission_by_location = get_analysis_data_by_location(
            self, data_points, locations
        )
        emission_by_scope, total_emissions = process_emission_by_scope(data_points)
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

        report_status = 1
        client_id = request.user.client.id
        user_id = request.user.id

        new_report = serializer.save(
            status=report_status,
            client_id=client_id,
            user_id=user_id,
            last_updated_by=request.user,
        )
        report_id = new_report.id
        success_response = Response(
            {"message": f"Report created successfully ID:{report_id}"},
            status=status.HTTP_200_OK,
        )
        esg_report_validation_string = create_validation_method_for_report_creation(
            report=new_report
        )
        if esg_report_validation_string is not None:
            return Response(
                data={
                    "message": {
                        "report_type": "esg_report",
                        "data": esg_report_validation_string,
                    },
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_report.report_type == "canada_bill_s211_v2":
            if not is_canada_bill_s211_v2_completed(
                user=request.user,
                organization=serializer.validated_data.get("organization"),
                corporate=serializer.validated_data.get("corporate"),
                year=serializer.validated_data["end_date"].year,
            ):
                new_report.delete()
                return Response(
                    data={
                        "message": {
                            "report_type": "canada_bill_s211_v2",
                            "data": "Canada Bill S211 v2 is not completed.",
                        },
                        "status": status.HTTP_400_BAD_REQUEST,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")
        corporate_id = serializer.validated_data.get("corporate")
        organization = serializer.validated_data.get("organization")
        report_by = serializer.validated_data.get("report_by")
        report_type = serializer.validated_data.get("report_type")
        investment_corporates = serializer.validated_data.get("investment_corporates")
        assessment_id = request.data.get("assessment_id")
        organization_id = organization.id
        if new_report.report_type != "canada_bill_s211_v2":
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
        else:
            return Response(
                {
                    "id": new_report.id,
                    "start_date": new_report.start_date,
                    "end_date": new_report.end_date,
                    "country_name": serializer.data.get("organization_country"),
                    "organization_name": new_report.organization.name,
                    "report_by": new_report.report_by,
                    "message": "None",
                    "report_type": new_report.report_type,
                    "created_at": format_created_at(serializer.data.get("created_at")),
                    "name": serializer.data.get("name"),
                },
                status=status.HTTP_200_OK,
            )

        if report_by == "Organization":
            common_name = organization.name
        else:
            common_name = corporate_id.name
        if (
            report_type
            in ["GRI Report: In accordance With", "GRI Report: With Reference to"]
        ) and assessment_id:
            ReportAssessment.objects.create(
                report_id=report_id,
                materiality_assessment_id=assessment_id,
            )

        if report_type == "GRI Report: With Reference to":
            return Response(
                {
                    "id": serializer.data.get("id"),
                    "start_date": serializer.data.get("start_date"),
                    "end_date": serializer.data.get("end_date"),
                    "country_name": serializer.data.get("organization_country"),
                    "organization_name": organization.name,
                    "report_by": report_by,
                    "message": f"Report created successfully ID:{report_id}",
                    "report_type": serializer.validated_data["report_type"],
                    "created_at": format_created_at(serializer.data.get("created_at")),
                    "name": serializer.data.get("name"),
                },
                status=status.HTTP_200_OK,
            )

        if report_type == "Custom ESG Report":
            validator = CustomEsgReportValidator()
            validator.create_custom_report(
                report_id,
                request.data.get("include_management_material_topics"),
                request.data.get("include_content_index"),
            )

        if (
            report_type == "GRI Report: In accordance With"
            or report_type == "GRI Report: With Reference to"
        ) and assessment_id:
            return Response(
                {
                    "id": serializer.data.get("id"),
                    "start_date": serializer.data.get("start_date"),
                    "end_date": serializer.data.get("end_date"),
                    "country_name": serializer.data.get("organization_country"),
                    "organization_name": organization.name,
                    "report_by": report_by,
                    "message": f"Report created successfully ID:{report_id}",
                    "report_type": serializer.validated_data["report_type"],
                    "created_at": format_created_at(serializer.data.get("created_at")),
                    "name": serializer.data.get("name"),
                },
                status=status.HTTP_200_OK,
            )

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
                    "created_at": format_created_at(serializer.data.get("created_at")),
                    "name": serializer.data.get("name"),
                },
                status=analysis_data.status_code,
            )
        return success_response


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

                if "ownership_ratio" in corporate_data:
                    ownership_ratio = corporate_data.get("ownership_ratio", None)
                    organized_data["ownership_ratio"] = ownership_ratio

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
        user = self.request.user
        organizations = user.orgs.all()

        if not user:
            return Report.objects.none()

        queryset = Report.objects.filter(organization__in=organizations, status=1)
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
                # Get blob client for the default logo
                blob_client = BlobClient.from_connection_string(
                    conn_str=settings.AZURE_STORAGE_CONNECTION_STRING,
                    container_name="media",
                    blob_name="sustainext.jpeg",
                )

                # Download the default logo blob content
                blob_data = blob_client.download_blob()

                # Save the blob content to the instance's logo field
                instance.org_logo.save(
                    "sustainext.jpeg", ContentFile(blob_data.readall()), save=True
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
        serializer.save(last_updated_by=self.request.user)


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


class ReportExistsView(APIView):
    def get(self, request):
        start = self.request.query_params.get("start_date")
        end = self.request.query_params.get("end_date")
        organization = self.request.query_params.get("organization", None)
        corporate = self.request.query_params.get("corporate", None)
        report_type = self.request.query_params.get("report_type", None)
        report_by = self.request.query_params.get("report_by", None)

        queryset = Report.objects.filter(
            organization=organization if organization else None,
            corporate=corporate if corporate else None,
            start_date=start,
            end_date=end,
            report_type=report_type,
            report_by=report_by,
        )

        if queryset.exists():
            return Response(
                {
                    "message": "Report Found",
                    "organization": Organization.objects.get(id=organization).name
                    if organization
                    else "",
                    "corporate": Corporateentity.objects.get(id=corporate).name
                    if corporate
                    else "",
                }
            )

        return Response(
            {
                "message": "No reports found",
                "organization": Organization.objects.get(id=organization).name
                if organization
                else "",
                "corporate": Corporateentity.objects.get(id=corporate).name
                if corporate
                else "",
            }
        )
