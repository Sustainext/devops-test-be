from datametric.models import DataPoint, RawResponse, Path, DataMetric, EmissionAnalysis
import requests
import logging
import os
import json
from datametric.data_types import ARRAY_OF_OBJECTS
import decimal
from django.template.defaultfilters import slugify
from django.core.mail import EmailMessage

from django.conf import settings
from sustainapp.models import ClientTaskDashboard
import uuid
from datetime import datetime
from azurelogs.time_utils import get_current_time_ist
from azurelogs.azure_log_uploader import AzureLogUploader
import time
from common.utils.data_point_cache import (
    delete_data_point_cache,
)


uploader = AzureLogUploader()

logger = logging.getLogger("django")
climatiq_logger = logging.getLogger("climatiq_logger")

calculate_emission_by_emissionfactor = os.getenv("CLIMATIQ_CALCULATION_BY_ID", "True")
data_version = os.getenv("CLIMATIQ_DATA_VERSION", "^16")


def process_dynamic_response(response):
    output = []

    for entry in response:
        # Iterate dynamically through all keys and values in the dictionary
        for key, value in entry.items():
            if isinstance(value, dict):  # Handle nested dictionaries
                output.append(f"{key.capitalize()}:")
                for nested_key, nested_value in value.items():
                    output.append(
                        f"  {nested_key.replace('_', ' ').capitalize()}: {nested_value}"
                    )
            elif isinstance(value, list):  # Handle lists if present
                output.append(f"{key.capitalize()}: {', '.join(map(str, value))}")
            else:  # Handle simple key-value pairs
                output.append(f"{key.replace('_', ' ').capitalize()}: {value}")

    # Add current date information
    current_date = datetime.now().strftime("%A, %B %d, %Y, %I %p %Z")
    output.append(f"Current Date: {current_date}")

    # Join the output with vertical splitters
    return " | ".join(output)


class Climatiq:
    """
    Climatiq is a class that calculates the batch data of emissions.
    Data is stored in the DataPoint model.
    Data is fetched from RawResponse model.
    """

    def __init__(self, raw_response: RawResponse) -> None:
        self.user = raw_response.user
        self.raw_response: RawResponse = raw_response
        self.client = raw_response.user.client
        self.locale = raw_response.locale
        self.month = raw_response.month
        self.year = raw_response.year
        self.index_mapping_to_emissons = {}

    def send_error_email(self, error_message):
        """
        Sends an error email using Django's email system.
        """
        subject = "Climatiq API Error"
        message = f"An error occurred in the Climatiq API:\n\n{error_message}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = settings.ADMIN_MAIL

        try:
            EmailMessage(subject, message, from_email, recipient_list).send()
            logger.info("Error email sent successfully")

            logger.info("Error email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send error email: {str(e)}")

    def neglect_missing_row(self, data_to_process):
        """
        Neglects the missing row in the data.
        """
        processed_data = []
        required_fields = [
            "Category",
            "Subcategory",
            "Activity",
            "activity_id",
            "unit_type",
            "Unit",
            "Quantity",
        ]
        # mapping the indexes to the emission from raw response
        for index, emission_data in enumerate(data_to_process):
            row_type = emission_data["Emission"].get("rowType")
            emission = emission_data["Emission"]

            # if a rowType is assigned or rowType is not present
            # we can neglect calculating the emission for it
            if not row_type or row_type in ["default", "approved", "calculated"]:
                if any(not emission.get(field) for field in required_fields):
                    # if the rowType is not present then mark it as default
                    if not row_type:
                        self.raw_response.data[index]["Emission"]["rowType"] = "default"
                    continue

                # if the Unit2 is present but Quantity2 is not present then we can neglect calculating the emission for it, vice versa is also true
                unit2 = emission.get("Unit2")
                quantity2 = emission.get("Quantity2")

                # Check for inconsistent Unit2 and Quantity2 entries
                if bool(quantity2) != bool(unit2):
                    if not row_type:
                        self.raw_response.data[index]["Emission"]["rowType"] = "default"
                    continue
                self.index_mapping_to_emissons.update({index: emission_data})
                processed_data.append(emission_data)
        return processed_data

    def payload_preparation_for_climatiq_api(self):
        """
        Prepares the payload for the climatiq api.
        """
        payload = []

        data_to_process = self.raw_response.data
        # remove the emissions where mandatory fields are missing
        processed_data = self.neglect_missing_row(data_to_process)

        if processed_data != []:
            for emission_data in processed_data:
                """
                Example of emission data:
                OrderedDict([('Emission',
                OrderedDict([('Category', 'Mobile Combustion'),
                                ('Subcategory', 'Road Travel'),
                                ('Activity',
                                'Bus - (EPA) - PassengerOverDistance'),
                                ('activity_id',
                                'passenger_vehicle-vehicle_type_bus-fuel_source_na-distance_na-engine_size_na'),
                                ('unit_type', 'PassengerOverDistance'),
                                ('Quantity', '323'),
                                ('Quantity2', '23'),
                                ('Unit2', 'km'),
                                ('Unit', 'passengers')]))])]
                """

                payload.append(
                    self.construct_emission_req(
                        activity_id=emission_data["Emission"]["activity_id"],
                        id=emission_data["Emission"]["act_id"]
                        if emission_data["Emission"].get("act_id")
                        else None,
                        unit_type=emission_data["Emission"]["unit_type"],
                        value1=float(emission_data["Emission"]["Quantity"]),
                        unit1=emission_data["Emission"]["Unit"],
                        unit2=emission_data["Emission"].get("Unit2"),
                        value2=(
                            float(emission_data["Emission"].get("Quantity2"))
                            if emission_data["Emission"].get("Quantity2")
                            not in [None, ""]
                            else None
                        ),
                    )
                )
            return payload
        else:
            return []

    def construct_emission_req(
        self, activity_id, id, unit_type, value1, unit1, value2=None, unit2=None
    ):
        emission_req = {
            "emission_factor": {},
            "parameters": {},
        }

        if calculate_emission_by_emissionfactor == "True":
            emission_req["emission_factor"] = {"id": id}
        else:
            emission_req["emission_factor"] = {
                "activity_id": activity_id,
                "data_version": f"^{data_version}",
            }

        unit_type = unit_type.lower()

        param_structures = {
            "area": {"area": value1, "area_unit": unit1},
            "areaovertime": {
                "area": value1,
                "area_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
            "containeroverdistance": {
                "twenty_foot_equivalent": value2,
                "distance": value1,
                "distance_unit": unit2,
            },
            "data": {"data": value1, "data_unit": unit1},
            "dataovertime": {
                "data": value1,
                "data_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
            "distance": {"distance": value1, "distance_unit": unit1},
            "distanceovertime": {
                "distance": value1,
                "distance_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
            "energy": {"energy": value1, "energy_unit": unit1},
            "money": {"money": value1, "money_unit": unit1},
            "number": {"number": int(value1)},
            "numberovertime": {"number": value1, "time": value2, "time_unit": unit2},
            "passengeroverdistance": {
                "passengers": int(value1),
                "distance": value2,
                "distance_unit": unit2,
            },
            "time": {"time": value1, "time_unit": unit1},
            "volume": {"volume": value1, "volume_unit": unit1},
            "weight": {"weight": value1, "weight_unit": unit1},
            "weightoverdistance": {
                "weight": value1,
                "weight_unit": unit1,
                "distance": value2,
                "distance_unit": unit2,
            },
            "weightovertime": {
                "weight": value1,
                "weight_unit": unit1,
                "time": value2,
                "time_unit": unit2,
            },
        }

        if unit_type in param_structures:
            emission_req["parameters"] = param_structures[unit_type]

        return emission_req

    def get_climatiq_api_response(self):
        """
        Returns the response from the climatiq api.
        """
        start_time = time.time()
        CLIMATIQ_AUTH_TOKEN: str | None = os.getenv("CLIMATIQ_AUTH_TOKEN")
        payload = self.payload_preparation_for_climatiq_api()
        headers = {"Authorization": f"Bearer {CLIMATIQ_AUTH_TOKEN}"}
        logger.info("Requesting Climatiq API")
        # print(payload, ' is payload for Climatiq')
        payload_log = process_dynamic_response(payload)
        org = self.user.orgs.first().name
        time_now = get_current_time_ist()
        all_response_data = []
        batch_size = 100

        for i in range(0, len(payload), batch_size):
            batch_payload = payload[i : i + batch_size]
            response = requests.request(
                "POST",
                url="https://api.climatiq.io/data/v1/estimate/batch",
                data=json.dumps(batch_payload),
                headers=headers,
            )
            response_data = response.json()
            if response.status_code == 400:
                self.log_error_climatiq_api(response_data=response_data)
            else:
                self.log_in_part_emission_error(
                    response_data=response_data, payload=payload
                )
                cleaned_response_data = self.clean_response_data(
                    batch_raw_response=self.raw_response.data[i : i + batch_size],
                    response_data=response_data,
                )
                all_response_data.extend(cleaned_response_data)

        # Update raw_response.data rowType based on calculated responses
        self.update_row_type_in_raw_response(all_response_data)
        # print(all_response_data, ' is the response from climatiq')
        log_data = process_dynamic_response(all_response_data)
        climatiq_logger.info(
            f"Request to Climatiq API took {time.time() - start_time} seconds"
        )

        log_data = [
            {
                "EventType": "Collect",
                "TimeGenerated": time_now,
                "EventDetails": "Emissions",
                "Action": "Calculated",
                "Status": "Success",
                "UserEmail": self.user.email,
                "UserRole": self.user.custom_role.name,
                "Logs": log_data,
                "Organization": org,
                "IPAddress": "192.168.1.1",
            },
        ]
        # orgs = user_instance.orgs
        uploader.upload_logs(log_data)
        climatiq_logger.info(f"Time took to upload logs: {time.time() - start_time}")
        return all_response_data

    def update_row_type_in_raw_response(self, response_data):
        """
        Updates rowType to 'calculated' in raw_response.data for successfully calculated emissions.
        Tracks the number of comparisons and matches for each index.
        """
        start_time = time.time()
        # Define the fields to compare
        fields_to_compare = [
            ("Category", "Category"),
            ("Subcategory", "SubCategory"),
            ("Activity", "Activity"),
            ("activity_id", "emission_factor.activity_id"),
            ("Quantity", "Quantity"),
            ("Unit", "Unit"),
            ("Unit2", "Unit2"),
            ("Quantity2", "Quantity2"),
        ]

        # Initialize a dictionary to track comparison counts
        comparison_results = {}

        # Helper function to normalize values for comparison
        def normalize(value):
            if value is None:
                return ""
            if isinstance(value, (int, float)):
                return str(value)
            if isinstance(value, str):
                return value.strip()
            return str(value)

        climatiq_logger.info(
            f"Length of response_data: {len(response_data)}, Length of self.index_mapping_to_emissons: {len(self.index_mapping_to_emissons)}"
        )
        for emission_data in response_data:
            for idx, object_emission in list(self.index_mapping_to_emissons.items()):
                emission = object_emission.get("Emission", {})

                # Initialize counts for this index if not present
                if idx not in comparison_results:
                    comparison_results[idx] = {
                        "total_comparisons": 0,
                        "matches": 0,
                        "mismatches": 0,
                    }

                # Count the comparison
                comparison_results[idx]["total_comparisons"] += 1

                matches = True

                for field1, field2 in fields_to_compare:
                    value1 = normalize(emission.get(field1))
                    value2 = normalize(self._get_nested_value(emission_data, field2))

                    # Treat empty strings and None as equivalent
                    if (
                        value1 == ""
                        and value2 is None
                        or value2 == ""
                        and value1 is None
                    ):
                        continue

                    # Compare values
                    if value1 != value2:
                        matches = False

                if matches:
                    # Update rowType to 'calculated'
                    self.raw_response.data[idx]["Emission"]["rowType"] = "calculated"

                    # Update ClientTaskDashboard if 'id' is present
                    if object_emission.get("id"):
                        try:
                            ctd = ClientTaskDashboard.objects.get(
                                id=object_emission.get("id")
                            )
                            ctd.roles = 4
                            ctd.task_status = "completed"
                            ctd.save()
                        except Exception as e:
                            climatiq_logger.error(
                                f"Failed to update ClientTaskDashboard for ID {object_emission.get('id')}: {e}"
                            )

                    # Remove the processed item
                    del self.index_mapping_to_emissons[idx]

                    # Increment match count
                    comparison_results[idx]["matches"] += 1

                else:
                    # Increment mismatch count and log details
                    comparison_results[idx]["mismatches"] += 1

        # Update the database with the modified raw_response
        RawResponse.objects.filter(id=self.raw_response.id).update(
            data=self.raw_response.data
        )
        end_time = time.time()

        # Log the summary
        climatiq_logger.info(
            f"Time took to compare: {round((end_time - start_time), 4)} seconds"
        )

        # Return the dictionary with comparison stats
        return comparison_results

    def _get_nested_value(self, data, key):
        """
        Helper method to get nested dictionary values using dot notation.
        Handles missing keys gracefully.
        """
        keys = key.split(".")
        value = data
        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None
            return value
        except Exception as e:
            climatiq_logger.error(
                f"Failed to access nested key '{key}' in data: {data}. Error: {e}"
            )
            return None

    def clean_response_data(self, batch_raw_response, response_data):
        """
        Cleans the response data from the climatiq api.
        TODO: Create a separate method for adding data.
        """
        cleaned_response_data = []
        self.refined_raw_resp = self.neglect_missing_row(batch_raw_response)
        for index, emission_data in enumerate(response_data["results"]):
            if "error" not in emission_data.keys():
                emission_data["Category"] = self.refined_raw_resp[index]["Emission"][
                    "Category"
                ]
                emission_data["SubCategory"] = self.refined_raw_resp[index]["Emission"][
                    "Subcategory"
                ]
                emission_data["Activity"] = self.refined_raw_resp[index]["Emission"][
                    "Activity"
                ]
                emission_data["Quantity"] = self.refined_raw_resp[index]["Emission"][
                    "Quantity"
                ]
                emission_data["Unit"] = self.refined_raw_resp[index]["Emission"].get(
                    "Unit"
                )
                emission_data["Quantity2"] = self.refined_raw_resp[index][
                    "Emission"
                ].get("Quantity2")

                emission_data["Unit2"] = self.refined_raw_resp[index]["Emission"].get(
                    "Unit2"
                )
                emission_data["unique_id"] = self.refined_raw_resp[index][
                    "Emission"
                ].get("unique_id")
                emission_data["scope"] = self.refined_raw_resp[index]["Emission"].get(
                    "scope"
                )
                logger.info(f"Emission data: {emission_data}")
                cleaned_response_data.append(emission_data)
        return cleaned_response_data

    def log_error_climatiq_api(self, response_data):
        """
        Logs the error response from the climatiq api.
        """
        error_message = f"Error with emission: {response_data} \n"
        self.send_error_email(error_message)

    def log_in_part_emission_error(self, response_data, payload=None):
        """
        Logs the error response from the climatiq api.
        """
        for index, emission_data in enumerate(response_data["results"]):
            if "error" in emission_data:
                details = {
                    "user": self.raw_response.user.username,
                    "raw_response_id": self.raw_response.id,
                    "scope": self.raw_response.path.slug,
                    # * Get the complete folder path.
                    "instance": os.path.abspath(__file__),
                }
                # update the  raw_response's emissions to rowType = default where error is present
                found_index = list(self.index_mapping_to_emissons.items())[index][0]
                self.raw_response.data[found_index]["Emission"]["rowType"] = "default"
                error_message = f"Error with emission: {emission_data} with data {payload[index]} \n Details for Debugging: {details}"

                self.send_error_email(error_message)

    def round_decimal_or_nulls(self, value, decimal_point=20):
        if not bool(value) and not isinstance(value, (int, float)):
            return None
        elif isinstance(value, str):
            return round(decimal.Decimal(value), decimal_point)
        else:
            return round(value, decimal_point)

    def create_emission_analysis(self, response_data):
        emission_analyse_bulk_list = []
        for index, emission in enumerate(response_data):
            emission_analyse = EmissionAnalysis(
                raw_response=self.raw_response,
                index=index,
                year=self.raw_response.year,
                month=self.raw_response.month,
                scope=(
                    "-".join(self.raw_response.path.slug.split("-")[-2:])
                ).capitalize(),
                emission_id=emission["emission_factor"]["id"],
                activity_id=emission["emission_factor"]["activity_id"],
                co2e_total=emission["co2e"],  # * This can also be None
                co2=self.round_decimal_or_nulls(
                    emission["constituent_gases"]["co2"], 20
                ),
                n2o=self.round_decimal_or_nulls(
                    emission["constituent_gases"]["n2o"], 20
                ),
                co2e_other=self.round_decimal_or_nulls(
                    emission["constituent_gases"]["co2e_other"], 20
                ),  # * This can also be None
                ch4=self.round_decimal_or_nulls(
                    emission["constituent_gases"]["ch4"], 20
                ),
                calculation_method=emission["co2e_calculation_method"],
                category=emission["Category"],
                subcategory=emission["SubCategory"],
                activity=f"{emission['Activity'].replace('(', '').replace(')', '')} - {emission['emission_factor']['region']} - {emission['emission_factor']['year']} - {emission['emission_factor']['source_lca_activity']}",
                region=emission["emission_factor"]["region"],
                name=emission["emission_factor"]["name"],
                unit=emission["activity_data"]["activity_unit"],
                consumption=self.round_decimal_or_nulls(
                    emission["activity_data"]["activity_value"]
                ),
                unit1=emission.get("Unit"),
                unit2=emission.get("Unit2"),
                quantity=self.round_decimal_or_nulls(emission.get("Quantity")),
                quantity2=self.round_decimal_or_nulls(emission.get("Quantity2")),
                type_of=emission["Activity"].split("-")[-1].strip(),
                unique_id=emission.get("unique_id"),
            )
            emission_analyse_bulk_list.append(emission_analyse)
        EmissionAnalysis.objects.bulk_create(emission_analyse_bulk_list)

    def modify_raw_response_with_uuid_and_scope(self):
        """
        Modifies the raw response with the uuid of the emission analysis.
        """
        scope_mapping = {
            "gri-environment-emissions-301-a-scope-1": "scope_1",
            "gri-environment-emissions-301-a-scope-2": "scope_2",
            "gri-environment-emissions-301-a-scope-3": "scope_3",
        }
        for emission_dict in self.raw_response.data:
            emission_dict["Emission"]["unique_id"] = str(uuid.uuid4())
            emission_dict["Emission"]["scope"] = scope_mapping.get(
                self.raw_response.path.slug
            )

    def create_calculated_data_point(self):
        """
        Returns the response from the climatiq api.
        """
        # Check if the path slug matches the required pattern

        if "gri-environment-emissions-301-a-scope-" not in self.raw_response.path.slug:
            return None
        logger.info("Climatiq API Has been called")
        logger.info("Original Response:")
        self.modify_raw_response_with_uuid_and_scope()
        logger.info(self.raw_response)
        # Get the response data from the climatiq API
        response_data = self.get_climatiq_api_response()
        if response_data is None:
            return None

        # Get or create the path
        try:
            path_new, created = Path.objects.get_or_create(
                name="GRI-Collect-Emissions-Scope-Combined",
                slug=slugify("GRI-Collect-Emissions-Scope-Combined"),
            )
            if created:
                path_new.save()
        except Exception as e:
            logger.error(f"An error occurred while getting or creating the path: {e}")
            return None

        # Get or create the data metric
        try:
            datametric, created = DataMetric.objects.get_or_create(
                name="CalculatedCollectedEmissions",
                label="Calculated Collected Emissions",
                description="Stores the calculated emissions from the GRI-Collect-Emissions-Scope-Combined",
                path=path_new,
                response_type="Array of Objects",
            )
            if created:
                datametric.save()
        except Exception as e:
            logger.error(
                f"An error occurred while getting or creating the data metric: {e}"
            )
            return None
        # Ensure datametric is not None
        if datametric is None:
            logger.error("Error: datametric is None")
            return None

        # Ensure raw_response has the required attributes
        if not hasattr(self.raw_response, "path"):
            logger.error("Error: raw_response has no path attribute")
            return None

        # Ensure location, year, month, user, and client attributes are present
        if (
            # self.location is None    commented on July18th
            self.locale is None
            or self.year is None
            or self.month is None
            or self.user is None
            or self.user.client is None
        ):
            logger.error(
                "Error: Missing required attributes (location, year, month, user, or user.client)"
            )
            return None
        logger.info(
            f"{datametric.name}{datametric.path.slug} -is the newly created datametric"
        )
        # Update or create the data point add this because we dont want to delete calculated datapoint instead we need to update it with new data
        try:
            datapoint, _ = DataPoint.objects.update_or_create(
                path=path_new,
                raw_response=self.raw_response,
                response_type=ARRAY_OF_OBJECTS,
                data_metric=datametric,
                is_calculated=True,
                locale=self.locale,
                year=self.year,
                month=self.month,
                user_id=self.user.id,
                client_id=self.user.client.id,
                metric_name=datametric.name,
                defaults={
                    "json_holder": response_data,
                },
            )

            delete_data_point_cache(
                datapoint.id
            )  # Deleting cache for this datapoint before its updated
            datapoint.save()
            self.create_emission_analysis(response_data=response_data)
        except Exception as e:
            print(f"An error occurred while creating or updating the data point: {e}")
            return None
