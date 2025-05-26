from analysis.models.Environment.GHGIntensity import GHGIntensity
from common.utils.value_types import get_float
from common.utils.getting_parameters_for_orgs_corps import (
    get_corporate,
    get_organisation,
)
from datametric.models import RawResponse
from django.db import transaction


def create_data_for_ghg_intensity_analysis(raw_response: RawResponse):
    if raw_response.path.slug != "gri-environment-emissions-GHG emission-intensity":
        return
    organisation = (
        raw_response.organization
        if get_organisation(raw_response.locale) is None
        else get_organisation(raw_response.locale)
    )
    corporate = (
        raw_response.corporate
        if get_corporate(raw_response.locale) is None
        else get_corporate(raw_response.locale)
    )
    location = raw_response.locale

    with transaction.atomic():
        GHGIntensity.objects.filter(raw_response=raw_response).delete()

        ghg_intensity_objects = []
        for index, local_data in enumerate(raw_response.data):
            ghg_intensity_objects.append(
                GHGIntensity(
                    raw_response=raw_response,
                    month=raw_response.month,
                    year=raw_response.year,
                    organisation=organisation,
                    corporate=corporate,
                    location=location,
                    client=raw_response.client,
                    index=index,
                    organization_specific_metric=local_data.get("MetricType"),
                    metric_name=local_data.get("Metricname"),
                    quantity=get_float(local_data.get("Quantity")),
                    unit=local_data.get("Units"),
                    types_included=local_data.get("intensityratio"),
                    custom_metric_type=local_data.get("customMetricType"),
                )
            )

        GHGIntensity.objects.bulk_create(ghg_intensity_objects)
