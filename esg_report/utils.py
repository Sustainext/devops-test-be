from sustainapp.models import Report, Corporateentity
from datametric.models import RawResponse, DataPoint, EmissionAnalysis
from esg_report.models.ContentIndexRequirementOmissionReason import (
    ContentIndexRequirementOmissionReason,
)
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from django.urls import reverse, resolve
from common.enums.GeneralTopicDisclosuresAndPaths import GENERAL_DISCLOSURES_AND_PATHS
from collections import defaultdict
import datetime
import logging
from django.db.models import Prefetch
from materiality_dashboard.Views.SDGMapping import SDG
from esg_report.models.ReportAssessment import ReportAssessment
from materiality_dashboard.models import (
    AssessmentDisclosureSelection,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)
from common.utils.report_datapoint_utils import (
    get_maximum_months_year,
    get_data_points_as_per_report,
)

logger = logging.getLogger("file")


def get_latest_raw_response(raw_responses, slug):
    return raw_responses.filter(path__slug=slug).order_by("-year").first()


def get_materiality_assessment(report):
    """This now uses ReportAssessment Model to fetch linked materiality assessment"""
    try:
        return ReportAssessment.objects.get(report=report).materiality_assessment
    except ReportAssessment.DoesNotExist:
        return None


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


def get_data_by_data_point_dictionary(data_points_dictionary, slug):
    return collect_data_by_raw_response_and_index(data_points_dictionary[slug])


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
        if response.status_code in [200, 206]:
            return response.data
        else:
            return {
                "detail": f"Error calling {view_url}: {response.status_code}: {response.data}"
            }

    except ValidationError as e:
        return {"detail": str(e)}
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
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
                return (
                    f"Data for disclosure {disclosure} does not exist for the report."
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


def generate_disclosure_status(
    report: Report, topic_mapping: dict, heading: str, is_material=False
):
    data_points = get_data_points_as_per_report(report=report)

    if is_material:
        # Nested output for material topics
        grouped_output = {}

        for _, data in topic_mapping.items():
            indicator = data["indicator"]
            subindicators = data["subindicators"]
            content_index_name = data["content_index_name"]
            heading2 = data.get("sub_header1", "Unknown Category")
            heading3 = data.get("sub_header2", "Unknown GRI")

            slugs = [slug for _, slug in subindicators]

            is_filled = all(
                data_points.filter(path__slug=slug).exclude(value="").exists()
                for slug in slugs
            )

            try:
                omission_reason = ContentIndexRequirementOmissionReason.objects.get(
                    report=report, indicator=indicator
                )
                reason = omission_reason.reason
                explanation = omission_reason.explanation
                is_filled = omission_reason.is_filled
            except ContentIndexRequirementOmissionReason.DoesNotExist:
                reason = None
                explanation = None

            item_data = {
                "key": indicator,
                "title": content_index_name,
                "page_number": None,
                "gri_sector_no": None,
                "is_filled": is_filled,
                "omission": [
                    {
                        "req_omitted": indicator if not is_filled else None,
                        "reason": reason,
                        "explanation": explanation,
                    }
                ],
            }

            grouped_output.setdefault(heading2, {}).setdefault(heading3, []).append(
                item_data
            )

        formatted_sections = []
        for heading2, heading3_dict in grouped_output.items():
            heading3_sections = []
            for heading3, items in heading3_dict.items():
                heading3_sections.append({"heading3": heading3, "items": items})
            formatted_sections.append(
                {"heading2": heading2, "sections": heading3_sections}
            )

        return {"heading1": heading, "sections": formatted_sections}

    else:
        # Flat output for general disclosures
        result = []

        for _, data in topic_mapping.items():
            indicator = data["indicator"]
            subindicators = data["subindicators"]
            content_index_name = data["content_index_name"]
            slugs = [slug for _, slug in subindicators]

            is_filled = all(
                data_points.filter(path__slug=slug).exclude(value="").exists()
                for slug in slugs
            )

            try:
                omission_reason = ContentIndexRequirementOmissionReason.objects.get(
                    report=report, indicator=indicator
                )
                reason = omission_reason.reason
                explanation = omission_reason.explanation
                is_filled = omission_reason.is_filled
            except ContentIndexRequirementOmissionReason.DoesNotExist:
                reason = None
                explanation = None

            result.append(
                {
                    "key": indicator,
                    "title": content_index_name,
                    "page_number": None,
                    "gri_sector_no": None,
                    "is_filled": is_filled,
                    "omission": [
                        {
                            "req_omitted": indicator if not is_filled else None,
                            "reason": reason,
                            "explanation": explanation,
                        }
                    ],
                }
            )

        return {"heading1": heading, "items": result}


def generate_disclosure_status_reference(
    report: Report,
    topic_mapping: dict,
    heading: str,
    is_material=False,
    filter_filled=False,
):
    """
    Generate a structured list of disclosure items for a given report, filtered by filled status.

    This function processes GRI indicators and their associated paths to determine which disclosures
    are fully completed (i.e., all required data points are filled). It filters out any disclosures
    that are incomplete and excludes omission information from the result.

    Args:
        report (Report): The report instance for which disclosures are being evaluated.
        topic_mapping (dict): A mapping of disclosure metadata, including indicator codes,
                              subindicators (slugs), and content titles.
        heading (str): The top-level heading label (e.g., "General Disclosures" or "Material Topics").
        is_material (bool, optional): Flag indicating whether the data pertains to material topics
                                      (grouped under subheadings) or general disclosures. Default is False.

    Returns:
        list: A list of dictionaries, each containing:
              - 'heading1': the disclosure section title
              - 'items': a list of disclosure entries with fields:
                  - 'key': indicator code (e.g., "2-1")
                  - 'title': disclosure title
                  - 'page_number': always None
                  - 'gri_sector_no': always None
                  - 'is_filled': True

              Only disclosures where all required subindicators are filled are included.
              The 'omission' field is excluded from the output.
    """
    data_points = get_data_points_as_per_report(report=report)

    if is_material:
        grouped_result = {}

        for _, data in topic_mapping.items():
            indicator = data["indicator"]
            subindicators = data["subindicators"]
            content_index_name = data["content_index_name"]
            heading1 = data.get("sub_header2", heading)

            slugs = [slug for _, slug in subindicators]

            is_filled = all(
                data_points.filter(path__slug=slug).exclude(value="").exists()
                for slug in slugs
            )

            if not is_filled:
                continue

            item = {
                "key": indicator,
                "title": content_index_name,
                "page_number": None,
                "gri_sector_no": None,
                "is_filled": is_filled,
            }

            grouped_result.setdefault(heading1, []).append(item)

        # Format the final list
        output = []
        for heading1, items in grouped_result.items():
            output.append({"heading1": heading1, "items": items})

        return output

    else:
        # General disclosures – flat single heading
        result = []

        for _, data in topic_mapping.items():
            indicator = data["indicator"]
            subindicators = data["subindicators"]
            content_index_name = data["content_index_name"]
            slugs = [slug for _, slug in subindicators]

            is_filled = all(
                data_points.filter(path__slug=slug).exclude(value="").exists()
                for slug in slugs
            )

            if not is_filled:
                continue

            result.append(
                {
                    "key": indicator,
                    "title": content_index_name,
                    "page_number": None,
                    "gri_sector_no": None,
                    "is_filled": is_filled,
                }
            )

        return [{"heading1": heading, "items": result}]


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
    """
    This is specifically designed to get the Management Materiality Topics.
    It assumes that every Management Materiality Topic contains the data points
    with the metrics names : GRI33cd and GRI33e
    If only Organization is selected for reporting, then we check the organization
    for the data points, if no data is available, we check and return all the
    data for the corresponding corporate entites.
    If the Organization and Corporate is selected for reporting, then we check the
    organization and corporate.
    """
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


def get_materiality_dashbaord(report):
    """
    Retrieves materiality dashboard linked to an report.
    """
    try:
        materiality_data = ReportAssessment.objects.get(
            report=report
        ).materiality_assessment
    except ReportAssessment.DoesNotExist:
        return []
    if materiality_data:
        selected_material_topics = materiality_data.selected_topics.prefetch_related(
            Prefetch(
                "topic__disclosure_set",  # Accessing disclosures for each topic
                to_attr="prefetched_disclosures",  # Store the result in a prefetched attribute
            )
        ).select_related("topic")
        grouped_by_esg_category = defaultdict(list)
        topic_selection_ids = selected_material_topics.values_list("id", flat=True)
        selected_disclosures = AssessmentDisclosureSelection.objects.filter(
            topic_selection__id__in=topic_selection_ids
        ).select_related("topic_selection", "disclosure")
        selected_disclosure_ids = set(
            selected_disclosures.values_list("disclosure_id", flat=True)
        )
        # Iterate and bifurcate by esg_category
        for selected_material_topic in selected_material_topics:
            item = {
                "name": selected_material_topic.topic.name,
                "esg_category": selected_material_topic.topic.esg_category,
                "identifier": selected_material_topic.topic.identifier,
                "disclosure": [
                    {
                        "name": disclosure.description.split(" ")[0],
                        "category": disclosure.category,
                        "show_on_table": disclosure.category
                        != "topic_management_dislcosure",
                        "relevent_sdg": SDG.get(disclosure.description.split(" ")[0]),
                    }
                    for disclosure in selected_material_topic.topic.prefetched_disclosures
                    if disclosure.id in selected_disclosure_ids
                ],
            }
            # Group by esg_category
            grouped_by_esg_category[selected_material_topic.topic.esg_category].append(
                item
            )

        grouped_by_esg_category = dict(grouped_by_esg_category)
    else:
        grouped_by_esg_category = []
    return grouped_by_esg_category
