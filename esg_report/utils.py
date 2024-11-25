from sustainapp.models import Report, Corporateentity
from datametric.models import RawResponse, DataPoint, EmissionAnalysis
from materiality_dashboard.models import MaterialityAssessment
from esg_report.models.ContentIndexRequirementOmissionReason import (
    ContentIndexRequirementOmissionReason,
)
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db.models import Q, F, ExpressionWrapper, DurationField
from datetime import timedelta
from django.db.models.functions import Greatest, Least
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from django.urls import reverse, resolve
from common.enums.GeneralTopicDisclosuresAndPaths import GENERAL_DISCLOSURES_AND_PATHS
import random
from collections import defaultdict
import datetime
import logging

logger = logging.getLogger("error.log")


def get_latest_raw_response(raw_responses, slug):
    return raw_responses.filter(path__slug=slug).order_by("-year").first()


def get_maximum_months_year(report: Report):
    """
    Get the maximum months year from the given report's start and end dates.
    This function determines the year that has the maximum number of months between the report's start and end dates. If both dates are in the same year, it returns that year. Otherwise, it calculates the number of months in the start and end years and returns the year with the maximum number of months.

    Args:
        report (Report): The report object containing the start and end dates.

    Returns:
        int: The year with the maximum number of months between the report's start and end dates.
    """
    # Extracting start_date and end_date
    start_date = report.start_date
    end_date = report.end_date

    # Getting the years for start_date and end_date
    start_year = start_date.year
    end_year = end_date.year

    # If both dates are in the same year
    if start_year == end_year:
        return start_year

    # Months in the start year
    months_start_year = 12 - start_date.month + 1

    # Months in the end year
    months_end_year = end_date.month

    # Determine which year has the maximum months
    if months_start_year > months_end_year:
        return start_year
    elif months_start_year == months_end_year:
        return end_date.year
    else:
        return end_year


def get_raw_responses_as_per_report(report: Report):
    """
    Get RawResponses as per report.

    Situation in RawResponses.
    1. If corporate is given, then organization would also be given.
    2. If corporate is not given, then organization will be given.
    3. If corporate and organization are not given, then locale will be given.
    Now Create a filter for each of this.
    and then combine them.
    """
    raw_responses = RawResponse.objects.filter(client=report.client)
    if report.corporate:
        raw_responses = raw_responses.filter(
            Q(corporate=report.corporate) | Q(organization=report.organization)
        )
        raw_responses = raw_responses.filter(
            Q(locale__in=report.corporate.location.all()) | Q(locale=None)
        )
    elif report.organization:
        raw_responses = raw_responses.filter(
            Q(organization=report.organization)
            | Q(
                locale__in=report.organization.corporatenetityorg.all().values_list(
                    "location", flat=True
                )
            )
        )
    return raw_responses.filter(year=get_maximum_months_year(report))


def get_data_points_as_per_report(report: Report):
    """
    Get DataPoints as per report.
    """
    data_points = DataPoint.objects.filter(client_id=report.client.id)
    if report.corporate:
        data_points = data_points.filter(
            Q(corporate=report.corporate)
            | Q(organization=report.organization)
            | Q(locale__in=report.corporate.location.all())
            | Q(locale=None)
        )
    elif report.organization:
        data_points = data_points.filter(
            Q(organization=report.organization)
            | Q(
                locale__in=report.organization.corporatenetityorg.all().values_list(
                    "location", flat=True
                )
            )
        )

    return data_points.filter(year=get_maximum_months_year(report))


def get_emission_analysis_as_per_report(report: Report):
    """
    Get EmissionAnalysis Objects as per report.
    """
    emission_analysis_objects = EmissionAnalysis.objects.filter(
        raw_response__in=get_raw_responses_as_per_report(report)
    )

    return emission_analysis_objects


def get_materiality_assessment(report):
    materiality_assessment = MaterialityAssessment.objects.filter(
        client=report.client
    ).exclude(status="outdated")
    if report.corporate:
        materiality_assessment = materiality_assessment.filter(
            Q(corporate=report.corporate) | Q(organization=report.organization)
        )
    elif report.organization:
        materiality_assessment = materiality_assessment.filter(
            Q(organization=report.organization)
            | Q(corporate__in=report.organization.corporatenetityorg.all())
        )
    start_date = report.start_date
    end_date = report.end_date

    # Check if the report falls within any materiality assessment period
    within_assessment = materiality_assessment.filter(
        start_date__lte=end_date, end_date__gte=start_date
    ).order_by("-end_date")

    if within_assessment.exists():
        return within_assessment.first()
    else:
        # Calculate the overlap duration in days for each materiality assessment
        materiality_assessment = (
            materiality_assessment.annotate(
                overlap_start=Greatest(F("start_date"), start_date),
                overlap_end=Least(F("end_date"), end_date),
            )
            .annotate(
                overlap_duration=ExpressionWrapper(
                    F("overlap_end") - F("overlap_start"), output_field=DurationField()
                )
            )
            .filter(overlap_duration__gt=timedelta(days=0))
            .order_by("-overlap_duration", "-end_date")
        )

        if materiality_assessment.exists():
            return materiality_assessment.first()
        else:
            return None


def collect_data_by_raw_response_and_index(data_points):
    # Create a dictionary where the key is raw_response and the value is another dictionary
    # which maps index to a dictionary of data_metric and value pairs
    raw_response_index_map = defaultdict(dict)

    # Iterate over the list of data points
    for dp in data_points:
        raw_response = dp.raw_response.id
        index = dp.index
        data_metric = dp.data_metric.name
        value = dp.value

        # Directly store the data_metric and value for the combination of raw_response and index
        raw_response_index_map[(raw_response, index)][data_metric] = value

    # Convert the defaultdict values into a list of dictionaries (the collected data)
    return list(raw_response_index_map.values())


def collect_data_and_differentiate_by_location(data_points):
    # Dictionary to store data grouped by raw_response and index (ignoring location for grouping)
    raw_response_index_map = defaultdict(dict)

    # Set to store unique locations
    unique_locations = set()

    # Iterate over the list of data points
    for dp in data_points:
        raw_response = dp.raw_response.id
        index = dp.index
        data_metric = dp.data_metric.name
        value = dp.value
        location = (
            dp.locale.name if dp.locale else None
        )  # Assuming locale represents location name

        # Store the data_metric and its value for the current raw_response and index
        raw_response_index_map[(raw_response, index)][data_metric] = value

        # Collect unique locations
        unique_locations.add(location)

    # Convert raw_response_index_map to a list of dictionaries (ignoring location for grouping)
    grouped_data = list(raw_response_index_map.values())

    # Return the grouped data and the list of unique locations
    response_data = {"data": grouped_data, "locations": list(unique_locations)}

    return response_data


# * A method that filters the data points based on the slug and data_point queryset given in parameter and then calls collect_data_by_raw_response_and_index method
def get_data_by_raw_response_and_index(data_points, slug):
    data_points = data_points.filter(
        path__slug=slug,
    )
    return collect_data_and_differentiate_by_location(data_points)


def forward_request_with_jwt(view_class, original_request, url, query_params):
    try:
        """
        Calls another internal API view with the JWT token from the original request.

        Args:
            view_class: The class-based view to be called.
            original_request: The original request object (HttpRequest).
            url: The URL of the internal API.
            query_params: Dictionary of query parameters to be passed to the internal API.

        Returns:
            Response: The response from the called internal API.
        """
        # Step 1: Extract the Authorization header from the original request
        auth_header = original_request.headers.get("Authorization", None)

        if not auth_header:
            return ValidationError(
                {"detail": "Authentication credentials were not provided."}, status=401
            )

        # Step 2: Create an APIRequestFactory instance to simulate the internal request
        factory = APIRequestFactory()

        # Step 3: Generate a GET request with query parameters and the Authorization header
        internal_request = factory.get(
            url,
            query_params,
            HTTP_AUTHORIZATION=auth_header,  # Pass the token from the original request
        )

        # Step 4: Call the class-based view's `as_view` method with the internal request
        view = view_class.as_view()
        temp = view(internal_request)
        # Step 5: Return the response from the internal view
        return temp.data
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


def calling_analyse_view_with_params(view_url, request, report):
    """
    Calls another internal API view with the JWT token from the original request.
    """
    try:
        # Step 1: Resolve the view
        resolved_view = resolve(reverse(view_url))
        view = resolved_view.func.view_class

        # Step 2: Prepare query parameters
        query_params = {
            "organisation": f"{report.organization.id}",
            "corporate": report.corporate.id if report.corporate is not None else "",
            "location": "",  # Empty string
            "start": report.start_date.strftime("%Y-%m-%d"),
            "end": report.end_date.strftime("%Y-%m-%d"),
        }

        # Step 3: Extract the JWT token from the original request
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            raise ValidationError(
                {"detail": "Authentication credentials were not provided."}, code=401
            )

        # Step 4: Create an APIRequestFactory instance to simulate the internal request
        factory = APIRequestFactory()
        internal_request = factory.get(
            reverse(view_url),
            query_params,
            HTTP_AUTHORIZATION=auth_header,  # Pass the token from the original request
        )

        # Step 5: Call the class-based view's `as_view` method with the internal request
        view_instance = view.as_view()
        response = view_instance(internal_request)

        # Step 6: Check the response status and return data
        if response.status_code == 200:
            return response.data
        else:
            return {"detail": f"Error calling {view_url}: {response.status_code}"}

    except ValidationError as e:
        return {"detail": str(e)}
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exec_info=True)
        return None


def creating_material_topic_and_disclosure():
    material_topic_and_disclosure = {
        "GRI Reporting info": [
            "Org Details",
            "Entities",
            "Report Details",
            "Restatement",
            "Assurance",
        ],
        "Organization Details": [
            "Business Details",
            "Workforce-Employees",
            "Workforce-Other Workers",
        ],
        "Compliance": ["Laws and Regulation"],
        "Membership & Association": ["Membership & Association"],
        "Stakeholder Engagement": ["Stakeholder Engagement"],
        "Collective Bargaining Agreements": ["Collective Bargaining Agreements"],
    }
    from materiality_dashboard.models import MaterialTopic, Disclosure
    from sustainapp.models import Framework

    f = Framework.objects.get(name="GRI: In Accordance With")
    for material_topic, disclosure in material_topic_and_disclosure.items():
        material_topic_obj, created = MaterialTopic.objects.get_or_create(
            name=material_topic,
            framework=f,
            esg_category="general",
        )
        material_topic_obj.save()
        for dis in disclosure:
            Disclosure.objects.get_or_create(topic=material_topic_obj, description=dis)[
                0
            ].save()


def getting_all_general_sections(report: Report):
    """
    Retrieves all general sections for a given report.
    """
    data_points = get_data_points_as_per_report(report=report)


def create_validation_method_for_report_creation(report: Report):
    """
    Creates a validation method for report creation.
    """
    if report.report_type == "GRI Report: In accordance With":
        general_material_topics = [
            "Org Details",
            "Entities",
            "Report Details",
            "Restatement",
            "Assurance",
        ]
        subindicators = []
        for topic in general_material_topics:
            if topic in GENERAL_DISCLOSURES_AND_PATHS:
                subindicators.extend(
                    GENERAL_DISCLOSURES_AND_PATHS[topic]["subindicators"]
                )
        data_points = get_data_points_as_per_report(report=report)
        for disclosure, path_slug in subindicators:
            if not data_points.filter(path__slug=path_slug).exists():
                report.delete()
                raise DRFValidationError(
                    {
                        "detail": f"Data for disclosure {disclosure} does not exist for the report."
                    }
                )


def calling_analyse_view_with_params_for_same_year(view_url, request, report):
    """
    Calls another internal API view with the JWT token from the original request.
    """
    try:
        # Step 1: Resolve the view
        resolved_view = resolve(reverse(view_url))
        view = resolved_view.func.view_class
        year = get_maximum_months_year(report=report)
        # Step 2: Prepare query parameters
        query_params = {
            "organisation": f"{report.organization.id}",
            "corporate": report.corporate.id if report.corporate is not None else "",
            "location": "",  # Empty string
            "start": datetime.datetime(year=year, month=1, day=1).strftime("%Y-%m-%d"),
            "end": datetime.datetime(year=year, month=12, day=31).strftime("%Y-%m-%d"),
        }

        # Step 3: Extract the JWT token from the original request
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            raise ValidationError(
                {"detail": "Authentication credentials were not provided."}, code=401
            )

        # Step 4: Create an APIRequestFactory instance to simulate the internal request
        factory = APIRequestFactory()
        internal_request = factory.get(
            reverse(view_url),
            query_params,
            HTTP_AUTHORIZATION=auth_header,  # Pass the token from the original request
        )

        # Step 5: Call the class-based view's `as_view` method with the internal request
        view_instance = view.as_view()
        response = view_instance(internal_request)

        # Step 6: Check the response status and return data
        if response.status_code == 200:
            return response.data
        else:
            return {"detail": f"Error calling {view_url}: {response.status_code}"}

    except ValidationError as e:
        return {"detail": str(e)}
    except Exception as e:
        logger.warning(f"An error occurred: {str(e)}", exc_info=True)
        return None


def get_which_general_disclosure_is_empty(report: Report):
    """
    Retrieves the general disclosures that are empty for a given report.
    """
    data_points = get_data_points_as_per_report(report=report)
    general_disclosures_and_paths = GENERAL_DISCLOSURES_AND_PATHS

    empty_sub_indicators = []
    for disclosure, indicator in general_disclosures_and_paths.items():
        for sub_indicator_and_path in indicator:
            if not data_points.filter(path__slug=sub_indicator_and_path[1]).exists():
                empty_sub_indicators.append(sub_indicator_and_path)
    return empty_sub_indicators


def generate_disclosure_status(report: Report):
    data_points = get_data_points_as_per_report(report=report)
    result = []
    for section_title, data in GENERAL_DISCLOSURES_AND_PATHS.items():
        indicator = data["indicator"]
        subindicators = data["subindicators"]
        content_index_name = data["content_index_name"]
        # Collect all slugs from subindicators
        slugs = []
        for title, slug in subindicators:
            slugs.append(slug)

        # Check if any slug has data
        is_filled = all(data_points.filter(path__slug=slug).exists() for slug in slugs)

        # Set page_number and gri_sector_no to None as per your requirements
        page_number = None
        gri_sector_no = None

        # Use the section title as the title
        title = content_index_name
        try:
            content_index_reason = ContentIndexRequirementOmissionReason.objects.get(
                report=report, indicator=indicator
            )
            reason = content_index_reason.reason
            explanation = content_index_reason.explanation
            is_filled = content_index_reason.is_filled
        except ContentIndexRequirementOmissionReason.DoesNotExist:
            content_index_reason = None
            reason = None
            explanation = None
            is_filled = is_filled
        # Append the dictionary to the result list
        result.append(
            {
                "key": indicator,
                "title": title,
                "page_number": page_number,
                "gri_sector_no": gri_sector_no,
                "is_filled": is_filled,
                "omission": [
                    {
                        "req_omitted": (f"{indicator}" if not is_filled else None),
                        "reason": reason,
                        "explanation": explanation,
                    }
                ],
            }
        )
    return result


def management_materiality_topics_common_code(dps, org_or_corp_name):
    necessary = {"GRI33cd": "", "GRI33e": ""}
    indexed_data = {}
    for dp in dps:
        if dp.raw_response.id not in indexed_data:
            indexed_data[dp.raw_response.id] = {}
        if dp.metric_name in necessary:
            if dp.index not in indexed_data[dp.raw_response.id]:
                indexed_data[dp.raw_response.id][dp.index] = {}
            indexed_data[dp.raw_response.id][dp.index][dp.metric_name] = dp.value
        else:
            logger.info(
                f"Materiality Management Topic : The metric name {dp.metric_name} is not in the necessary list"
            )

    grouped_data = []
    for i_key, i_val in indexed_data.items():
        for k, v in i_val.items():
            temp_data = {
                "GRI33cd": v.get("GRI33cd", ""),
                "GRI33e": v.get("GRI33e", ""),
                "org_or_corp": org_or_corp_name,
            }
            if temp_data not in grouped_data:
                grouped_data.append(temp_data)

    return grouped_data


def get_management_materiality_topics(report: Report, path):

    year = get_maximum_months_year(report)

    mmt_dps = DataPoint.objects.filter(
        organization=report.organization,
        corporate=report.corporate,
        # locale=report.locale if report.locale else None,
        client_id=report.client.id,
        path__slug=path,
        year=year,
    )

    if not mmt_dps:
        logger.error(
            f"No DataPoints found for path :{path} in organiztion {report.organization} and corporate {report.corporate}"
        )

        if not report.corporate:
            corps_of_org = Corporateentity.objects.filter(
                organization=report.organization
            )
            if not corps_of_org:
                logger.error(
                    f"No Corporate Entities found for organiztion {report.organization}"
                )
                return []
            res = []
            for a_corp in corps_of_org:
                dps = DataPoint.objects.filter(
                    organization=report.organization,
                    corporate=a_corp,
                    # locale=report.locale if report.locale else None,
                    client_id=report.client.id,
                    path__slug=path,
                    year=year,
                )
                if dps:
                    res.extend(
                        management_materiality_topics_common_code(dps, a_corp.name)
                    )
            return res

    return management_materiality_topics_common_code(mmt_dps, report.organization.name)
