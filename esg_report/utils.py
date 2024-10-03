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
