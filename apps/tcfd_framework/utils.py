from collections import defaultdict


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
