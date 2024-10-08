from sustainapp.models import Report
from materiality_dashboard.models import MaterialityAssessment
from rest_framework.exceptions import ValidationError
from django.db.models import Q, F, ExpressionWrapper, DurationField
from django.db.models.functions import ExtractMonth
from datetime import timedelta


def get_latest_raw_response(raw_responses, slug):
    return raw_responses.filter(path__slug=slug).order_by("-year").first()


def get_materiality_assessment(report: Report):
    """
    The duration is to be calculated by the report.
    So Imagine there are two materiality dashboards m and n
    m = (start_date,end_date)=(1st January 2022, 31st December 2022)
    n = (start_date,end_date) = (1st January 2023, 31st December 2023)
    Now Imagine there are two reports r1 and r2
    r1 = (start_date, end_date) = (1st November 2022, 1st June 2023)
    r2 = (start_date, end_date) = (1st June 2022, 31st January 2023)
    r1 will use materiality dashboard n r2 will use materiality dashboard m
    Because the report period lies more in the period of n materiality dashboard.
    """
    materiality_assessment = MaterialityAssessment.objects.filter(
        client=report.client,
    )
    start_date = report.start_date
    end_date = report.end_date

    # Check if the report falls within any materiality assessment period
    within_assessment = materiality_assessment.filter(
        start_date__gte=start_date, end_date__lte=end_date
    ).order_by("-end_date")

    if within_assessment.exists():
        return within_assessment.first()
    else:
        # Calculate the overlap duration in days for each materiality assessment
        materiality_assessment = (
            materiality_assessment.annotate(
                overlap_start=ExpressionWrapper(
                    F("start_date") if F("start_date") > start_date else start_date,
                    output_field=DurationField(),
                ),
                overlap_end=ExpressionWrapper(
                    F("end_date") if F("end_date") < end_date else end_date,
                    output_field=DurationField(),
                ),
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
