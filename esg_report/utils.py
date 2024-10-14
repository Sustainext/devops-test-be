from sustainapp.models import Report
from datametric.models import RawResponse, DataMetric, DataPoint
from materiality_dashboard.models import MaterialityAssessment
from rest_framework.exceptions import ValidationError
from django.db.models import Q, F, ExpressionWrapper, DurationField
from datetime import timedelta
from django.db.models.functions import Greatest, Least
from django.core.exceptions import ValidationError


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
            Q(corporate=report.corporate)
            | Q(corporate=None)
            | Q(organization=report.organization)
            | Q(organization=None)
        )
        raw_responses = raw_responses.filter(
            Q(locale__in=report.corporate.location.all()) | Q(locale=None)
        )
        return raw_responses
    elif report.organization:
        raw_responses = raw_responses.filter(
            Q(organization=report.organization)
            | Q(organization=None)
            | Q(corporate__in=report.organization.corporatenetityorg.all())
            | Q(corporate=None)
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
            | Q(corporate=None)
            | Q(organization=report.organization)
            | Q(organization=None)
        )
        data_points = data_points.filter(
            Q(locale__in=report.corporate.location.all()) | Q(locale=None)
        )
        return data_points
    elif report.organization:
        data_points = data_points.filter(
            Q(organization=report.organization)
            | Q(organization=None)
            | Q(corporate__in=report.organization.corporatenetityorg.all()) | Q(corporate=None)
        )
    return data_points.filter(year=get_maximum_months_year(report))


def get_materiality_assessment(report):
    materiality_assessment = MaterialityAssessment.objects.filter(client=report.client)
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
            raise ValidationError("Materiality Assessment not found")
