from apps.canada_bill_s211.v2.models.ReportingForEntities import ReportingForEntities
from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from apps.canada_bill_s211.v2.constants import SUBMISSION_INFORMATION, REPORTING_FOR_ENTITIES
from sustainapp.models import Organization, Corporateentity
from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError as DrfValidationError

def _default_response(total_screens:int, data:list):
    existing_screens = {item['screen'] for item in data}
    for screen in range(1, total_screens + 1):
        if screen not in existing_screens:
            data.append({'screen': screen, 'status': 'incomplete'})
    data.sort(key=lambda x: x['screen'])
    return data

def get_status_report_data(filters: dict):
    """
    Retrieves and processes status report data for ReportingForEntities and SubmissionInformation.

    Args:
        filters: A dictionary of filters to apply to the queries.

    Returns:
        A tuple containing two lists: reporting_for_entities_response and submission_information_response.
    """

    reporting_for_entities = ReportingForEntities.objects.filter(**filters)
    reporting_for_entities_response = list(reporting_for_entities.values("screen","status"))
    submission_information = SubmissionInformation.objects.filter(**filters)
    submission_information_response = list(submission_information.values("screen","status"))

    reporting_for_entities_response = _default_response(
        total_screens=REPORTING_FOR_ENTITIES,
        data=reporting_for_entities_response
    )
    submission_information_response = _default_response(
        total_screens=SUBMISSION_INFORMATION,
        data=submission_information_response
    )

    return reporting_for_entities_response, submission_information_response


def is_canada_bill_s211_v2_completed(user, organization: Organization, corporate: Corporateentity | None, year:int):
    """
    Checks if Canada Bill S211 v2 is completed.

    Returns:
        True if Canada Bill S211 v2 is completed, False otherwise.
    """
    # Check if user has access to the organization
    if not user.orgs.filter(id=organization.id).exists():
        raise DrfValidationError("You do not have access to this organization.")

    # Check if user has access to the corporate (if provided)
    if corporate is not None and not user.corps.filter(id=corporate.id).exists():
        raise DrfValidationError("You do not have access to this corporate.")
    filters = {
        "organization": organization,
        "year": year,
        "organization__client": user.client,
    }
    if corporate:
        filters["corporate"] = corporate
    reporting_for_entities_response, submission_information_response = get_status_report_data(filters)
    if all([i["status"] == "completed" for i in reporting_for_entities_response + submission_information_response]):
        return True
    return False
