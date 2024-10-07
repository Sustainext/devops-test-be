from sustainapp.models import Report
from materiality_dashboard.models import MaterialityAssessment
from rest_framework.exceptions import ValidationError


def get_latest_raw_response(raw_responses, slug):
    return raw_responses.filter(path__slug=slug).order_by("-year").first()


def get_materiality_dashboard(report: Report):
    ...