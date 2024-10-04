from sustainapp.models import Report
from materiality_dashboard.models import MaterialityAssessment
from rest_framework.exceptions import ValidationError


def get_latest_raw_response(raw_responses, slug):
    return raw_responses.filter(path__slug=slug).order_by("-year").first()


def get_materiality_dashboard(report: Report):
    """
    x < a,  y < b :
    Case 1 - [Previous Materiality Exists] Use the material topics from m₁ OR the previous materiality assessment done within the dates where 'x' and 'y' fall.
    Case 2 - [Previous Materiality does not exist] Validation needs to be shown that no material topics have been selected for the chosen dates. User cannot proceed without selecting material topics.

    x < a,  y > b : Use the material topics from m₂.

    x > a,  y < b : Use the material topics from m₂.

    x > a,  y > b :
    Case 1 (if x<b) -  Use the material topics from m₂, show message that "Start and end date chosen for the report fall outside the dates applicable to the current Materiality Assessment. Proceed with the most recent material topics?"

    Case 2 (if x>b) - Validation needs to be shown that no material topics have been selected for the chosen dates. User cannot proceed without selecting material topics.
    """
    ...
    x, y = report.start_date, report.end_date
    current_materiality = (
        MaterialityAssessment.objects.filter(client=report.client)
        .order_by("-created_at")
        .first()
    )
    a, b = current_materiality.start_date, current_materiality.end_date
    previous_materiality = (
        MaterialityAssessment.objects.filter(client=report.client)
        .filter(id__gt=current_materiality.id)
        .order_by("-created_at")
        .first()
    )

    if x < a and y < b:
        if (
            previous_materiality
            and previous_materiality.start_date <= x <= previous_materiality.end_date
            and previous_materiality.start_date <= y <= previous_materiality.end_date
        ):
            # Case 1: Previous materiality exists within the date range
            return previous_materiality
        else:
            # Case 2: No previous materiality exists
            raise ValidationError(
                "No material topics have been selected for the chosen dates. User cannot proceed."
            )

    elif (x < a and y > b) or (x > a and y < b):
        # Use material topics from the current materiality assessment
        return current_materiality

    elif x > a and y > b:
        if x < b:
            # Case 1: Use the most recent material topics with a message
            return current_materiality
        else:
            # Case 2: Validation failure due to no topics selected
            raise ValidationError(
                "No material topics have been selected for the chosen dates. User cannot proceed."
            )

    else:
        return "No valid condition matched."
