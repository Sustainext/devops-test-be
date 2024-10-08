from sustainapp.models import Report
from materiality_dashboard.models import MaterialityAssessment
from rest_framework.exceptions import ValidationError
from django.db.models import Q, F, ExpressionWrapper, DurationField
from datetime import timedelta
from django.db.models.functions import Greatest, Least
from django.core.exceptions import ValidationError


def get_latest_raw_response(raw_responses, slug):
    return raw_responses.filter(path__slug=slug).order_by("-year").first()


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
