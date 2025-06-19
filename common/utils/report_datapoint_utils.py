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

logger = logging.getLogger("file")



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
