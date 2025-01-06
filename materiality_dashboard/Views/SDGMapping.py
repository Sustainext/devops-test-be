all_sdgs = [
    {"name": "SDG-1", "text_color": "#ffffff", "bg_color": "#ea1d2d"},
    {"name": "SDG-2", "text_color": "#ffffff", "bg_color": "#d19f2a"},
    {"name": "SDG-3", "text_color": "#ffffff", "bg_color": "#4c9f38"},
    {"name": "SDG-4", "text_color": "#ffffff", "bg_color": "#c22033"},
    {"name": "SDG-5", "text_color": "#ffffff", "bg_color": "#ea580c"},
    {"name": "SDG-6", "text_color": "#ffffff", "bg_color": "#198038"},
    {"name": "SDG-7", "text_color": "#ffffff", "bg_color": "#fbbf24"},
    {"name": "SDG-8", "text_color": "#ffffff", "bg_color": "#7f1d1d"},
    {
        "name": "SDG-9",
        "text_color": "#ffffff",
        "bg_color": "#004c3f",
    },  # Color not found
    {"name": "SDG-10", "text_color": "#ffffff", "bg_color": "#e01a83"},
    {"name": "SDG-11", "text_color": "#ffffff", "bg_color": "#00689d"},
    {"name": "SDG-12", "text_color": "#ffffff", "bg_color": "#ca8a04"},
    {"name": "SDG-13", "text_color": "#ffffff", "bg_color": "#365314"},
    {"name": "SDG-14", "text_color": "#ffffff", "bg_color": "#007dbc"},
    {"name": "SDG-15", "text_color": "#ffffff", "bg_color": "#40ae49"},
    {"name": "SDG-16", "text_color": "#ffffff", "bg_color": "#1e3a8a"},
    {
        "name": "SDG-17",
        "text_color": "#ffffff",
        "bg_color": "#00689d",
    },  # Color not found
]


def get_sdg_details(sdg_names):
    sdg_map = {sdg["name"]: sdg for sdg in all_sdgs}
    return [sdg_map[sdg_name] for sdg_name in sdg_names if sdg_name in sdg_map]


common_sdgs_305 = get_sdg_details(["SDG-3", "SDG-12", "SDG-13", "SDG-14", "SDG-15"])
common_sdgs_302 = get_sdg_details(["SDG-7", "SDG-8", "SDG-12", "SDG-13"])
sdg_306_1 = get_sdg_details(["SDG-3", "SDG-6", "SDG-11", "SDG-12"])
sdg_306_2 = get_sdg_details(["SDG-3", "SDG-6", "SDG-8", "SDG-11", "SDG-12"])
sdg_306_3_and_5 = get_sdg_details(["SDG-3", "SDG-6", "SDG-11", "SDG-12", "SDG-15"])
sdg_306_4 = get_sdg_details(["SDG-3", "SDG-11", "SDG-12"])
common_sdgs_301 = get_sdg_details(["SDG-8", "SDG-12"])
sdg_303_1_and_2 = get_sdg_details(["SDG-6", "SDG-12"])
sdg_303_3_and_4_and_5 = get_sdg_details(["SDG-6"])

SDG = {
    "305-1": common_sdgs_305,
    "305-2": common_sdgs_305,
    "305-3": common_sdgs_305,
    "302-1": common_sdgs_302,
    "302-2": common_sdgs_302,
    "302-3": common_sdgs_302,
    "302-4": common_sdgs_302,
    "302-5": common_sdgs_302,
    "306-1": sdg_306_1,
    "306-2": sdg_306_2,
    "306-3": sdg_306_3_and_5,
    "306-4": sdg_306_4,
    "306-5": sdg_306_3_and_5,
    "301-1": sdg_306_3_and_5,
    "301-2": sdg_306_3_and_5,
    "301-3": sdg_306_3_and_5,
    "303-1": sdg_303_1_and_2,
    "303-2": sdg_303_1_and_2,
    "303-3": sdg_303_3_and_4_and_5,
    "303-4": sdg_303_3_and_4_and_5,
    "303-5": sdg_303_3_and_4_and_5,
    "401-1": get_sdg_details(["SDG-5", "SDG-8", "SDG-10"]),
    "401-2": get_sdg_details(["SDG-3", "SDG-5", "SDG-8"]),
    "401-3": get_sdg_details(["SDG-5", "SDG-8"]),
    "402-1": get_sdg_details(["SDG-8"]),
    "403-1": get_sdg_details(["SDG-8"]),
    "403-2": get_sdg_details(["SDG-8"]),
    "403-3": get_sdg_details(["SDG-8"]),
    "403-4": get_sdg_details(["SDG-8", "SDG-16"]),
    "403-5": get_sdg_details(["SDG-8"]),
    "403-6": get_sdg_details(["SDG-3"]),
    "403-7": get_sdg_details(["SDG-8"]),
    "403-8": get_sdg_details(["SDG-8"]),
    "403-9": get_sdg_details(["SDG-3", "SDG-8", "SDG-16"]),
    "403-10": get_sdg_details(["SDG-3", "SDG-8", "SDG-16"]),
    "404-1": get_sdg_details(["SDG-4", "SDG-5", "SDG-8", "SDG-10"]),
    "404-2": get_sdg_details(["SDG-8"]),
    "404-3": get_sdg_details(["SDG-5", "SDG-8", "SDG-10"]),
    "405-1": get_sdg_details(["SDG-5", "SDG-8", "SDG-10"]),
    "406-1": get_sdg_details(["SDG-5", "SDG-8"]),
    "407-1": get_sdg_details(["SDG-8"]),
    "408-1": get_sdg_details(["SDG-5", "SDG-8", "SDG-16"]),
    "409-1": get_sdg_details(["SDG-5", "SDG-8"]),
    "410-1": get_sdg_details(["SDG-16"]),
    "411-1": get_sdg_details(["SDG-2"]),
    "413-1": get_sdg_details(["SDG-1", "SDG-2"]),
    "413-2": get_sdg_details(["SDG-1", "SDG-2"]),
    "414-1": get_sdg_details(["SDG-5", "SDG-8", "SDG-16"]),
    "414-2": get_sdg_details(["SDG-5", "SDG-8", "SDG-16"]),
    "415-1": get_sdg_details(["SDG-16"]),
    "416-1": get_sdg_details(["SDG-16"]),
    "416-2": get_sdg_details(["SDG-16"]),
    "417-1": get_sdg_details(["SDG-12"]),
    "417-2": get_sdg_details(["SDG-16"]),
    "418-1": get_sdg_details(["SDG-16"]),
}
