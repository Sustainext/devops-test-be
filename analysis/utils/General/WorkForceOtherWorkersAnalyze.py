from datametric.models import RawResponse
from analysis.models.General.WorkForceOtherWorkers import GeneralWorkersNotEmp
from analysis.models.Social.Gender import Gender
from common.utils.value_types import get_float


def create_data(raw_response: RawResponse):

    for index, response_item in enumerate(raw_response.data):
        GeneralWorkersNotEmp.objects.update_or_create(
            raw_response=raw_response,
            month=raw_response.month,
            year=raw_response.year,
            location=raw_response.locale,
            organisation=raw_response.organization,
            corporate=raw_response.corporate,
            client=raw_response.client,
            index=index,
            defaults={
                "type_of_worker": (
                    response_item.get("TypeofWorker")
                    if response_item.get("TypeofWorker") != "Others (please specify)"
                    else response_item.get("TypeofWorker_others")
                ),
                "total_workers": get_float(response_item.get("TotalnumberofWorkers")),
                "contractual_relationship": (
                    response_item.get("Contractualrelationship")
                    if response_item.get("Contractualrelationship")
                    != "Others (please specify)"
                    else response_item.get("Contractualrelationship_others")
                ),
                "work_performed": (
                    response_item.get("Workperformed")
                    if response_item.get("Workperformed") != "Others (please specify)"
                    else response_item.get("Workperformed_others")
                ),
                "engagement_approach": response_item.get("Engagementapproach"),
                "third_party": (
                    response_item.get("Thirdparty")
                    if response_item.get("Thirdparty") != "Others (please specify)"
                    else response_item.get("Thirdparty_others")
                ),
            },
        )[0].save()


def workforce_other_workers_analysis(raw_response: RawResponse):
    if raw_response.path.slug != "gri-general-workforce_other_workers-workers-2-8-a":
        return
    GeneralWorkersNotEmp.objects.filter(raw_response=raw_response).delete()
    create_data(raw_response)
