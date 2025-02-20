from datametric.models import RawResponse


def get_prev_form_data(location, year):
    path_slug = "gri-environment-air-quality-ods_production-import-export"
    organization = location.corporateentity.organization
    corporate = location.corporateentity

    raw_data = RawResponse.objects.filter(
        path__slug=path_slug, year=year, organization=organization, corporate=None
    )

    corporate_raw_data = RawResponse.objects.filter(
        path__slug=path_slug, year=year, organization=organization, corporate=corporate
    )

    if corporate_raw_data.exists():
        raw_data = corporate_raw_data

    if not raw_data.exists():
        return None

    prev_form_data = [item for sublist in raw_data for item in sublist.data]
    return prev_form_data
