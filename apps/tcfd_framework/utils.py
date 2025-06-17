from collections import defaultdict
from django.core.cache import cache
from common.utils.sanitise_cache import sanitize_cache_key_part
from apps.tcfd_framework.models.TCFDCollectModels import (
    RecommendedDisclosures,
    SelectedDisclosures,
)


def get_tcfd_disclosures_response(
    disclosures_queryset, selected_disclosures_ids: None | list = None
):
    """
    Utility to format RecommendedDisclosures queryset into the required response structure.
    """
    order_mapping = {
        0: "a",
        1: "b",
        2: "c",
        3: "d",
        4: "e",
        5: "f",
        6: "g",
        7: "h",
        8: "i",
        9: "j",
        10: "k",
    }

    disclosures = disclosures_queryset.values(
        "core_element__id",
        "core_element__name",
        "core_element__description",
        "description",
        "order",
        "screen_tag",
        "id",
    )

    core_map = defaultdict(lambda: {"description": "", "disclosures": []})
    for d in disclosures:
        core_id = d["core_element__id"]
        core_map[core_id]["description"] = d["core_element__description"]
        core_map[core_id].setdefault("name", d["core_element__name"])
        core_map[core_id]["disclosures"].append(
            {
                "description": f"{order_mapping.get(d['order'], '')}) {d['description']}",
                "screen_tag": d["screen_tag"],
                "id": d["id"],
                "selected": (
                    selected_disclosures_ids is not None
                    and d["id"] in selected_disclosures_ids
                ),
            }
        )

    response = {
        core["name"]: {
            "description": core["description"],
            "disclosures": core["disclosures"],
        }
        for core in core_map.values()
    }
    return response


def get_or_set_tcfd_cache_data(organization, corporate):
    cache_key = f"tcfd_disclosures_{sanitize_cache_key_part(organization)}_{sanitize_cache_key_part(corporate)}"
    cached_data = cache.get(cache_key)
    if cached_data is None:
        selected_disclosures = SelectedDisclosures.objects.filter(
            organization=organization, corporate=corporate
        ).prefetch_related("recommended_disclosure")
        selected_disclosures_recommended_disclosure_ids = (
            selected_disclosures.values_list("recommended_disclosure__id", flat=True)
        )

        # * Get all important data
        disclosures = RecommendedDisclosures.objects.all().select_related(
            "core_element"
        )
        response_data = get_tcfd_disclosures_response(
            disclosures_queryset=disclosures,
            selected_disclosures_ids=selected_disclosures_recommended_disclosure_ids,
        )
        cache.set(cache_key, response_data, timeout=86400)
    else:
        response_data = cached_data
    return response_data


def update_selected_disclosures_cache(organization, corporate, recommended_disclosures):
    """
    Utility method to update the selected disclosures and cache for given organization and corporate.
    """
    cache_key = f"tcfd_disclosures_{sanitize_cache_key_part(organization)}_{sanitize_cache_key_part(corporate)}"
    cache.delete(cache_key)

    SelectedDisclosures.objects.filter(
        organization=organization,
        corporate=corporate,
    ).delete()

    SelectedDisclosures.objects.bulk_create(
        [
            SelectedDisclosures(
                recommended_disclosure=rd,
                organization=organization,
                corporate=corporate,
            )
            for rd in recommended_disclosures
        ]
    )
    response_data = get_tcfd_disclosures_response(
        disclosures_queryset=RecommendedDisclosures.objects.all().select_related(
            "core_element"
        ),
        selected_disclosures_ids=list(
            SelectedDisclosures.objects.filter(
                organization=organization, corporate=corporate
            ).values_list("recommended_disclosure__id", flat=True)
        ),
    )
    cache.set(cache_key, response_data, timeout=86400)
    return response_data
