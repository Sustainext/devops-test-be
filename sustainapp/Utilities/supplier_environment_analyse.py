import logging
from sustainapp.models import Corporateentity
from datametric.models import RawResponse

logger = logging.getLogger("error.log")


def calculate_percentage(org_name, corp_name, q1, q2=None, filter_for_corp=False):
    if not filter_for_corp:
        return {
            "org_or_corp": org_name if not corp_name else corp_name,
            "percentage": (q1 / q2) * 100 if q2 != 0 else 0,
        }
    else:
        return {
            "org_or_corp": corp_name,
            "percentage": (q1 / q2) * 100 if q2 != 0 else 0,
        }


def new_suppliers(org, corp, client_id, year, path, filter_by, filter_for_corp=False):
    lst = []

    sup_env_data = RawResponse.objects.filter(
        **filter_by,
        path__slug=path,
        client_id=client_id,
        year=year,
    ).first()

    if (
        sup_env_data
        and path == "gri-supplier_environmental_assessment-new_suppliers-308-1a"
    ):
        try:
            q1 = sup_env_data.data[0]["Q1"]
            q2 = sup_env_data.data[0]["Q2"]
            lst.append(
                calculate_percentage(
                    org.name,
                    corp.name if corp else None,
                    float(q1),
                    float(q2),
                    filter_for_corp=filter_for_corp,
                )
            )
        except Exception as e:
            logger.error(
                f"SupplierEnvironment.py > the exception {e} for the path {path}"
            )
            return []
        return lst

    elif sup_env_data and path in [
        "gri-supplier_environmental_assessment-negative_environmental-308-2d",
        "gri-supplier_environmental_assessment-negative_environmental-308-2e",
    ]:
        try:
            suppliers_assesed = (
                RawResponse.objects.filter(
                    **filter_by,
                    path__slug="gri-supplier_environmental_assessment-negative_environmental-308-2a",
                    client_id=client_id,
                    year=year,
                )
                .first()
                .data[0]["Q1"]
            )

            q1 = sup_env_data.data[0]["Q1"]
            lst.append(
                calculate_percentage(
                    org.name,
                    corp.name if corp else None,
                    float(q1),
                    float(suppliers_assesed),
                    filter_for_corp=filter_for_corp,
                )
            )
        except Exception as e:
            logger.error(
                f"SupplierEnvironment.py > the exception {e} for the path {path}"
            )
            return []
        return lst

    elif not sup_env_data and corp is None:
        corps_of_org = Corporateentity.objects.filter(organization=org)
        result = []
        for corporate in corps_of_org:
            logger.error(
                f"SupplierEnvironment.py > checking for the corporate {corporate.name} with the path {path}"
            )
            filtering = {
                "organization__id": org.id,
                "corporate__id": corporate.id,
            }
            k = new_suppliers(
                org, corporate, client_id, year, path, filtering, filter_for_corp=True
            )
            if k:
                result.extend(k)
        return result

    else:
        return []
