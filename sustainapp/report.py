import matplotlib, io, json, pycountry, time, base64
import matplotlib.pyplot as plt
from itertools import cycle
from .models import Report
from .serializers import AnalysisData2
from django.shortcuts import get_object_or_404
from django.contrib.staticfiles import finders
import logging
from django.conf import settings
import os
from django.templatetags.static import static
from django.core.files.storage import default_storage
from collections import defaultdict
from common.utils.value_types import format_decimal_places
import re
from decimal import Decimal

logger = logging.getLogger()


def generate_colors(num_colors):
    color_cycle = cycle(plt.cm.tab10.colors)
    colors = [next(color_cycle) for _ in range(num_colors)]
    return colors


def extract_donut_chart_data(combined_scopes):
    return [
        {"scope_name": scope_data["scope_name"], "total_co2e": scope_data["total_co2e"]}
        for scope_data in combined_scopes.values()
    ]


def generate_and_cache_donut_chart(data, investment_corporates=False):
    start_time = time.time()
    try:
        # Use the Agg backend
        matplotlib.use("Agg")

        if not investment_corporates:
            donut_labels = [entry["scope_name"] for entry in data]
            donut_data = [
                Decimal(format_decimal_places(entry["total_co2e"])) for entry in data
            ]
        else:
            donut_labels = [entry["corporate_name"] for entry in data]
            donut_data = [
                Decimal(format_decimal_places(entry["total_co2e"])) for entry in data
            ]

        # Auto-generating colors according to data length
        colors = generate_colors(len(data))

        # making Fig size Fixed
        radius_cm = 6
        figsize = (2 * radius_cm / 2.54, 2 * radius_cm / 2.54)

        fig, ax = plt.subplots(figsize=figsize, dpi=120)

        wedges, texts, autotexts = ax.pie(
            donut_data,
            autopct="",
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.3),
        )
        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

        # This is where you adjust the labels for the legend
        legend_labels = [
            "{0} - {1:.3f} ({2}%)".format(label, value, round(percentage, 1))
            for label, value, percentage in zip(
                donut_labels,
                donut_data,
                [d / sum(donut_data) * 100 for d in donut_data],
            )
        ]

        # Here we calculate the number of columns needed, assuming 5 items per column is a good fit.
        num_columns = len(legend_labels) // 5 + (1 if len(legend_labels) % 5 else 0)

        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

        # Move the legend to the right side
        ax.legend(
            wedges,
            legend_labels,
            title="Categories",
            loc="upper center",
            bbox_to_anchor=(0.5, -0.1),
            ncol=num_columns,
        )

        # Tight layout to minimize white space
        plt.tight_layout()

        # Convert the plot to a base64-encoded image
        image_data = io.BytesIO()
        plt.savefig(image_data, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)

        # Encode the image data as base64
        image_base64 = base64.b64encode(image_data.getvalue()).decode("utf-8")

        # Embed the base64 image directly in the HTML template
        html_content = (
            f'<img src="data:image/png;base64,{image_base64}" alt="Donut Chart">'
        )
        logging.info(f"Donut chart generated in {time.time() - start_time} seconds")
        return html_content
    except Exception as e:
        # Handle the exception gracefully
        logger.exception("Unexpected error generating Scope Chart")
        return None


def word_generate_and_cache_donut_chart(data):
    # Use the Agg backend
    matplotlib.use("Agg")

    donut_labels = [entry["scope_name"] for entry in data]
    donut_data = [entry["total_co2e"] for entry in data]

    # Auto-generating colors according to data length
    colors = generate_colors(len(data))

    fig, ax = plt.subplots(figsize=(4, 4), dpi=80)

    wedges, texts, autotexts = ax.pie(
        donut_data, autopct="", startangle=90, colors=colors, wedgeprops=dict(width=0.3)
    )
    plt.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

    chart_image = io.BytesIO()
    plt.savefig(chart_image, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(2, 1), dpi=120)  # Adjust size to fit your needs
    ax.axis("off")  # Turn off axis
    fig.legend(wedges, donut_labels, loc="center", ncol=3)  # Adjust columns as needed
    plt.tight_layout()

    legend_image = io.BytesIO()
    plt.savefig(legend_image, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    return chart_image, legend_image


def extract_source_data(organized_data_list):
    try:
        source_data = []
        investments_corporates_source_data = {
            "category_name": "",
            "activity_name": "",
            "total_co2e": 0.0,
        }
        for entry in organized_data_list:
            sources = entry.get("sources", [])
            for source in sources:
                source_entry = {
                    "category_name": source.get("category_name", "Unknown Source"),
                    "activity_name": source.get("activity_name", "Unknown Source"),
                    "total_co2e": float(source.get("total_co2e", 0.0)),
                }
                if entry.get("corporate_type") != "Investment":
                    source_data.append(source_entry)
                else:
                    # For investment corporates, we need to sum the total_co2e
                    investments_corporates_source_data["category_name"] = source_entry[
                        "category_name"
                    ]
                    investments_corporates_source_data["activity_name"] = source_entry[
                        "activity_name"
                    ]
                    investments_corporates_source_data["total_co2e"] += source_entry[
                        "total_co2e"
                    ]
        source_data.append(investments_corporates_source_data)
        return source_data
    except Exception as e:
        # Handle the exception gracefully
        logger.exception("Unexpected error generating Source Data")
        return None


def generate_and_cache_donut_chart_source(data):
    start_time = time.time()
    try:
        # Use the Agg backend
        matplotlib.use("Agg")

        # Filter data to exclude entries with 'total_co2e' less than 1
        filtered_data = [entry for entry in data if entry["total_co2e"] > 0]

        source_labels = [entry["category_name"] for entry in filtered_data]
        source_activity = [
            (
                entry["activity_name"].split("-")[0].strip()
                if entry["activity_name"] is not None
                else ""
            )
            for entry in filtered_data
        ]
        source_data = [entry["total_co2e"] for entry in filtered_data]

        # Exit early if no data meets the criteria
        if not source_data:
            return "No data with values greater than or equal to 1."

        # Auto-generating colors according to data length
        colors = generate_colors(len(data))

        # making Fig size Fixed
        radius_cm = 6
        figsize = (2 * radius_cm / 2.54, 2 * radius_cm / 2.54)

        fig, ax = plt.subplots(figsize=figsize, dpi=120)

        wedges, texts, autotexts = ax.pie(
            source_data,
            autopct="",
            labeldistance=1.25,
            pctdistance=1.05,
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.3),
        )

        # This is where you adjust the labels for the legend
        legend_labels = [
            "{0} - {1} ({2}%)".format(label, value, round(percentage, 1))
            for label, value, percentage in zip(
                source_labels,
                source_activity,
                [d / sum(source_data) * 100 for d in source_data],
            )
        ]

        # Here we calculate the number of columns needed, assuming 5 items per column is a good fit.
        num_columns = len(legend_labels) // 10 + (1 if len(legend_labels) % 50 else 0)

        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

        # Move the legend to the right side
        ax.legend(
            wedges,
            legend_labels,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.3),
            ncol=num_columns,
        )

        # Tight layout to minimize white space
        plt.tight_layout()

        # Convert the plot to a base64-encoded image
        image_data = io.BytesIO()
        plt.savefig(image_data, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)

        # Encode the image data as base64
        image_base64 = base64.b64encode(image_data.getvalue()).decode("utf-8")

        # Embed the base64 image directly in the HTML template
        html_content = (
            f'<img src="data:image/png;base64,{image_base64}" alt="Source Donut Chart">'
        )
        logging.info(
            f"Generated Source Donut Chart in {time.time() - start_time} seconds"
        )
        return html_content

    except Exception as e:
        # Handle the exception gracefully
        logger.exception("Unexpected error generating Source Chart")
        return None


def word_generate_and_cache_donut_chart_source(data):
    try:
        matplotlib.use("Agg")  # Set the backend to Agg for rendering to a buffer

        # Filter data entries with 'total_co2e' greater than 0
        filtered_data = [entry for entry in data if entry["total_co2e"] > 0]

        # Extract necessary details from data
        source_labels = [entry["category_name"] for entry in filtered_data]
        source_data = [entry["total_co2e"] for entry in filtered_data]

        # Exit early if no valid data exists
        if not source_data:
            return "No data with values greater than or equal to 1."

        # Generate a color palette
        colors = generate_colors(len(source_data))

        # Define the size of the figure
        radius_cm = 10
        figsize = (
            2 * radius_cm / 2.54,
            2 * radius_cm / 2.54,
        )  # Conversion from cm to inches

        # Create the pie chart
        fig, ax = plt.subplots(figsize=figsize, dpi=120)
        wedges, texts, autotexts = ax.pie(
            source_data,
            labels=None,
            autopct="",
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.3),
            pctdistance=0.85,
        )
        plt.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

        # Save the pie chart without labels
        chart_image = io.BytesIO()
        plt.savefig(chart_image, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)

        # Create a separate figure for the legend
        num_columns = len(source_labels) // 5 + (1 if len(source_labels) % 5 else 0)
        fig, ax = plt.subplots(figsize=(3, 2), dpi=120)  # Adjust size to fit your needs
        ax.axis("off")  # Turn off axis
        fig.legend(
            wedges, source_labels, loc="center", ncol=num_columns
        )  # Adjust columns as needed
        plt.tight_layout()

        # Save the legend only
        legend_image = io.BytesIO()
        plt.savefig(legend_image, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)

        return chart_image, legend_image

    except Exception as e:
        print(f"Unexpected error generating Source Chart: {e}")
        return None, None


def extract_location_data(organized_data_list):
    try:
        location_data = []
        for entry in organized_data_list:
            locations = entry.get("locations", [])
            for location in locations:
                location_entry = {
                    "location_name": location.get("location_name", "Unknown location"),
                    "total_co2e": float(
                        format_decimal_places(location.get("total_co2e", 0.0))
                    ),
                }
                location_data.append(location_entry)
        return location_data
    except Exception as e:
        # Handle the exception gracefully
        logger.exception("Unexpected error generating Location Data")
        return None


def generate_and_cache_donut_chart_location(data):
    start_time = time.time()
    try:
        # Use the Agg backend
        matplotlib.use("Agg")

        donut_labels = [entry["location_name"] for entry in data]
        donut_data = [entry["total_co2e"] for entry in data]

        # Auto-generating colors according to data length
        colors = generate_colors(len(data))

        # Fixed radius
        radius_cm = 6
        figsize = (2 * radius_cm / 2.54, 2 * radius_cm / 2.54)

        fig, ax = plt.subplots(figsize=figsize, dpi=120)

        wedges, texts, autotexts = ax.pie(
            donut_data,
            autopct="",
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.3),
        )
        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

        # This is where you adjust the labels for the legend
        legend_labels = [
            "{0} - {1:.3f} ({2}%)".format(label, value, round(percentage, 1))
            for label, value, percentage in zip(
                donut_labels,
                donut_data,
                [d / sum(donut_data) * 100 for d in donut_data],
            )
        ]

        # Here we calculate the number of columns needed, assuming 5 items per column is a good fit.
        num_columns = len(legend_labels) // 5 + (1 if len(legend_labels) % 5 else 0)

        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

        # Move the legend to the right side
        ax.legend(
            wedges,
            legend_labels,
            title="Categories",
            loc="upper center",
            bbox_to_anchor=(0.5, -0.1),
            ncol=num_columns,
        )
        # Tight layout to minimize white space
        plt.tight_layout()

        # Convert the plot to a base64-encoded image
        image_data = io.BytesIO()
        plt.savefig(image_data, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)

        # Encode the image data as base64
        image_base64 = base64.b64encode(image_data.getvalue()).decode("utf-8")

        # Embed the base64 image directly in the HTML template
        html_content = (
            f'<img src="data:image/png;base64,{image_base64}" alt="Donut Chart">'
        )
        logging.info(f"Location chart generated in {time.time() - start_time} seconds")
        return html_content
    except Exception as e:
        # Handle the exception gracefully
        logger.exception("Unexpected error generating Loacation Chart")
        return None


def word_generate_and_cache_donut_chart_location(data):
    try:
        # Use the Agg backend
        matplotlib.use("Agg")

        donut_labels = [entry["location_name"] for entry in data]
        donut_data = [entry["total_co2e"] for entry in data]

        # Auto-generating colors according to data length
        colors = generate_colors(len(data))

        # Fixed radius
        radius_cm = 10
        figsize = (2 * radius_cm / 2.54, 2 * radius_cm / 2.54)

        fig, ax = plt.subplots(figsize=figsize, dpi=120)

        wedges, texts, autotexts = ax.pie(
            donut_data,
            autopct="",
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.3),
        )
        plt.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.
        # Save the pie chart without labels
        chart_image = io.BytesIO()
        plt.savefig(chart_image, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)

        # Here we calculate the number of columns needed, assuming 5 items per column is a good fit.
        num_columns = len(donut_labels) // 5 + (1 if len(donut_labels) % 5 else 0)

        fig, ax = plt.subplots(figsize=(3, 2), dpi=120)  # Adjust size to fit your needs
        ax.axis("off")  # Turn off axis
        fig.legend(
            wedges, donut_labels, loc="center", ncol=num_columns
        )  # Adjust columns as needed
        plt.tight_layout()

        # Convert the plot to a base64-encoded image
        legend_image = io.BytesIO()
        plt.savefig(legend_image, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)

        return chart_image, legend_image

    except Exception as e:
        logging.exception("Unexpected error generating Loacation Chart")
        logging.exception(e)
        return None


def generate_pdf_data(pk):
    """
    For GHG with Investment, Scope 3 is the sum of scope 1 and scope 2. Scope 1 and 2 were only added for showing the information of invested corporates in a new table.
    """
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        raise Exception("Report does not exist")
    except Report.MultipleObjectsReturned:
        raise Exception("Multiple reports exist")

    country_code = report.organization.country

    if not country_code:
        country_name = "Unknown"
    else:
        try:
            # Attempt to get the country name from pycountry
            country_name = pycountry.countries.get(alpha_2=country_code).name
        except AttributeError:
            # Handle the case where the country_code is not found in pycountry
            country_name = "Unknown"

    # image_url = request.build_absolute_uri(staticfiles_storage.url('ghg-methodology-flowchart.png'))
    # image_path = finders.find("images/ghg-methodology-flowchart.png")
    image_path = default_storage.url("ghg-methodology-flowchart.png")

    data_entry = get_object_or_404(AnalysisData2, report_id=pk)

    # Deserialize the JSON string into a Python dictionary
    # data_dict = json.loads(data_entry.data.replace('\\"', '"'))
    try:
        data_dict = json.loads(data_entry.data.replace('\\"', '"'))
    except json.JSONDecodeError as e:
        logging.error("JSON Decode Error: {0}".format(e))

    organized_data_list = []
    total_co2e_combined = 0
    total_contribution_combined = 0
    combined_scopes = {}

    investment_corporates_data = {}
    has_investment_corporates = False
    investment_corporates_graph_data = []
    investment_corporates_scope12 = defaultdict(dict)
    investment_corporates_co2e = 0  # HOPIN THIS AIN'T NEEDED

    # Iterate over each corporate in data_dict
    for corporate_name, corporate_data in data_dict.items():
        # Extract data for each corporate
        scopes = corporate_data.get("scope", [])
        locations = corporate_data.get("location", [])
        sources = corporate_data.get("source", [])

        # Calculate total combined CO2e and total contribution for each corporate
        if corporate_data.get("corporate_type") == "Investment":
            has_investment_corporates = True
            # Invested corporates only consider Scope 3
            total_co2e_corporate = sum(
                float(scope["total_co2e"])
                for scope in scopes
                if scope["scope_name"] == "Scope-3"
            )

            total_contribution_corporate = sum(
                float(scope["contribution_scope"])
                for scope in scopes
                if scope["scope_name"] == "Scope-3"
            )
        else:
            total_co2e_corporate = sum(float(scope["total_co2e"]) for scope in scopes)

            # Calculate total contribution for all corporates
            total_contribution_corporate = sum(
                float(scope["contribution_scope"]) for scope in scopes
            )

        total_co2e_combined += total_co2e_corporate
        total_contribution_combined += total_contribution_corporate

        if corporate_data["corporate_type"] == "Investment":  # TIS AIN'T NEEDED
            investment_corporates_data[corporate_name] = (
                total_co2e_corporate  # TIS AIN'T NEEDED
            )

        # Calculate combined percentage for each scope within the corporate
        for scope in scopes:
            if (
                corporate_data.get("corporate_type") == "Investment"
                and scope["scope_name"] != "Scope-3"
            ):
                # Saving to show the investment table information
                investment_corporates_scope12[corporate_name][scope["scope_name"]] = (
                    float(scope["total_co2e"])
                )
                investment_corporates_scope12[corporate_name]["ownership_ratio"] = (
                    corporate_data["ownership_ratio"]
                )
                continue

            elif (
                corporate_data.get("corporate_type") == "Investment"
                and scope["scope_name"] == "Scope-3"
            ):
                # Investment corporate CO2e is from just Scope 3,
                # where scope 3 = (Scope 1 + Scope 2) * ownership_ratio
                # Saving to investment_corporates_graph_data to show the invested corporates in graph
                investment_corporates_graph_data.append(
                    {
                        "corporate_name": corporate_name,
                        "total_co2e": float(scope["total_co2e"]),
                    }
                )
            scope_name = scope["scope_name"]
            # if scope_name == 1:  # Check if the scope is 1
            #     total_co2e_scope1 += float(scope['total_co2e'])

            if scope_name not in combined_scopes:
                combined_scopes[scope_name] = {
                    "scope_name": scope_name,
                    "total_co2e": float(scope["total_co2e"]),
                    "contribution_scope": float(scope["contribution_scope"]),
                    "co2e_unit": scope["co2e_unit"],
                    # 'combined_percentage': (float(combined_scopes[scope_name]['total_co2e']) / total_co2e_combined) * 100 if total_co2e_combined != 0 else 0
                }
            else:
                combined_scopes[scope_name]["total_co2e"] += float(scope["total_co2e"])
                combined_scopes[scope_name]["combined_percentage"] = (
                    (
                        float(combined_scopes[scope_name]["total_co2e"])
                        / total_co2e_combined
                    )
                    * 100
                    if total_co2e_combined != 0
                    else 0
                )

        # After updating total_co2e for all scopes in the current corporate, calculate combined_percentage
        for scope_name, scope_data in combined_scopes.items():
            scope_data["combined_percentage"] = (
                (scope_data["total_co2e"] / total_co2e_combined) * 100
                if total_co2e_combined != 0
                else 0
            )
            # Convert the combined scopes back to a list if necessary
            # combined_scopes_list = list(combined_scopes.values())
            combined_scopes_list = sorted(
                combined_scopes.values(),
                key=lambda scope: int(re.search(r"\d+", scope["scope_name"]).group()),
            )
        # Organize the data
        scopes_sorted = sorted(scopes, key=lambda s: int(s["scope_name"].split("-")[1]))
        organized_data = {
            "corporate_name": corporate_name,
            "corporate_type": corporate_data["corporate_type"],
            "scopes": scopes_sorted,
            "locations": locations,
            "sources": sources,
        }
        organized_data_list.append(organized_data)

    if investment_corporates_data:
        for corporate_name, co2e_value in investment_corporates_data.items():
            investment_corporates_co2e += co2e_value

    if organized_data_list:
        highest_contribution_value = 0
        highest_source_name = None
        for item in organized_data_list:
            if item["sources"]:  # Check if item["sources"] is not empty
                highest_contribution_source_for_corporate = max(
                    item["sources"],
                    key=lambda x: float(x["contribution_source"]),
                )
                # Compare the numeric value instead of the dictionary
                if (
                    float(
                        highest_contribution_source_for_corporate["contribution_source"]
                    )
                    > highest_contribution_value
                ):
                    highest_contribution_value = float(
                        highest_contribution_source_for_corporate["contribution_source"]
                    )
                    highest_source_name = (
                        "Investments"
                        if item["corporate_type"] == "Investment"
                        else highest_contribution_source_for_corporate["source_name"]
                    )
    else:
        highest_source_name = None


    # Extract total_co2e and scope_name from combined_scopes# extracted_data = [{'scope_name': scope['scope_name'], 'total_co2e': scope['total_co2e']} for scope in combined_scopes.values()]
    donut_chart_data = extract_donut_chart_data(combined_scopes)

    # Call the function to generate donut chart HTML
    donut_chart_html = generate_and_cache_donut_chart(donut_chart_data)

    if has_investment_corporates:
        donut_chart_data_investment = (
            generate_and_cache_donut_chart(
                investment_corporates_graph_data, investment_corporates=True
            )
            if has_investment_corporates
            else None
        )

    # report_list_view, extract source data
    source_data = extract_source_data(organized_data_list)

    # Use the extracted source_data to generate the dynamic chart
    source_donut_chart_html = generate_and_cache_donut_chart_source(source_data)

    # report_list_view, extract Location data
    location_data = extract_location_data(organized_data_list)

    # Use the extracted Location_data to generate the dynamic chart
    location_donut_chart_html = generate_and_cache_donut_chart_location(location_data)

    organization_name = report.organization.name
    if report.report_by == "Organization":
        organization_name = organization_name
    else:
        organization_name = report.corporate.name

    updated_investment_corporates_scope12 = defaultdict(dict)
    for corporate_name, scopes in investment_corporates_scope12.items():
        for k, v in scopes.items():
            new_scope = (
                "scope1" if k == "Scope-1" else "scope2" if k == "Scope-2" else k
            )
            updated_investment_corporates_scope12[corporate_name][new_scope] = v
    context = {
        "object_list": report,
        "org_logo": report.org_logo if report.org_logo else None,
        "report_type": report.report_type,
        "report_by": report.report_by,
        "organization_name": organization_name,
        "country": country_name,
        "about_the_organization": report.about_the_organization,
        "roles_and_responsibilities": report.roles_and_responsibilities,
        "organizational_boundries": report.organizational_boundries,
        "excluded_sources": report.excluded_sources,
        "designation_of_organizational_admin": report.designation_of_organizational_admin,
        "reporting_period_name": report.reporting_period_name,
        "start_date": report.start_date,
        "end_date": report.end_date,
        "from_year": report.from_year,
        "to_year": report.to_year,
        "data_source": report.data_source,
        "calender_year": report.calender_year,
        "total_co2e_combined": round(total_co2e_combined, 2),
        "pk": pk,
        "data": organized_data_list,
        "combined_scopes": combined_scopes_list,
        "image_path": image_path,
        "highest_source_name": highest_source_name,
        "donut_chart_html": donut_chart_html,
        "source_donut_chart_html": source_donut_chart_html,
        "location_donut_chart_html": location_donut_chart_html,
        "has_investment_corporates": has_investment_corporates,
    }

    if has_investment_corporates:
        context["investment_corporates_scope12"] = dict(
            updated_investment_corporates_scope12
        )
        context["donut_chart_data_investment"] = (donut_chart_data_investment,)
    return context
