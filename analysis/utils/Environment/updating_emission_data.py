from django.db import connection
from django.db.utils import OperationalError
from datametric.models import RawResponse

SQL_SCRIPT = """
-- Create the table if it doesn't exist
CREATE TABLE IF NOT EXISTS emission_data (
    "Index" INTEGER,
    "Path ID" INTEGER,
    "Response ID" INTEGER,
    "Month" INTEGER,
    "Year" INTEGER,
    "Scope" TEXT,
    "Location ID" INTEGER,
    "Location of Operation" TEXT,
    "Corporate Entity" TEXT,
    "Organization" TEXT,
    "Client ID" INTEGER,
    "User ID" INTEGER,
    "CO2e (tonnes)" NUMERIC,
    "Category" TEXT,
    "Subcategory" TEXT,
    "Activity" TEXT,
    "Quantity" NUMERIC,
    "Unit" TEXT,
    "Quantity2" NUMERIC,
    "Unit2" TEXT
);

-- Insert data into the table
INSERT INTO emission_data
SELECT DISTINCT
    public.datametric_datapoint.index AS "Index",
    public.datametric_datapoint.path_id AS "Path ID",
    public.datametric_datapoint.raw_response_id AS "Response ID",
    public.datametric_datapoint.month AS "Month",
    public.datametric_datapoint.year AS "Year",
    substring(public.datametric_path.name from 'Scope-[0-9]+') AS "Scope",
    public.datametric_datapoint.locale_id AS "Location ID",
    locale.name AS "Location of Operation",
    corporate_entity.name AS "Corporate Entity",
    organization.name AS "Organization",
    public.datametric_datapoint.client_id AS "Client ID",
    public.datametric_datapoint.user_id AS "User ID",
    MAX(public.datametric_emissionanalysis.co2e_total) AS "CO2e (tonnes)",
    MAX(CASE WHEN public.datametric_datapoint.metric_name = 'Category' THEN public.datametric_datapoint.string_holder END) AS "Category",
    MAX(CASE WHEN public.datametric_datapoint.metric_name = 'Subcategory' THEN public.datametric_datapoint.string_holder END) AS "Subcategory",
    MAX(CASE WHEN public.datametric_datapoint.metric_name = 'Activity' THEN public.datametric_datapoint.string_holder END) AS "Activity",
    MAX(CASE WHEN public.datametric_datapoint.metric_name = 'Quantity' THEN public.datametric_datapoint.number_holder END) AS "Quantity",
    MAX(CASE WHEN public.datametric_datapoint.metric_name = 'Unit' THEN public.datametric_datapoint.string_holder END) AS "Unit",
    MAX(CASE WHEN public.datametric_datapoint.metric_name = 'Quantity2' THEN public.datametric_datapoint.number_holder END) AS "Quantity2",
    MAX(CASE WHEN public.datametric_datapoint.metric_name = 'Unit2' THEN public.datametric_datapoint.string_holder END) AS "Unit2"
FROM
    public.datametric_datapoint
JOIN
    public.datametric_path ON public.datametric_path.id = public.datametric_datapoint.path_id
JOIN
    public.datametric_rawresponse ON public.datametric_datapoint.raw_response_id = public.datametric_rawresponse.id
JOIN
    public.datametric_datametric ON public.datametric_datapoint.data_metric_id = public.datametric_datametric.id
JOIN
    public.authentication_client ON public.datametric_datapoint.client_id = public.authentication_client.id
JOIN
    public.sustainapp_location AS locale ON public.datametric_datapoint.locale_id = locale.id
JOIN
    public.sustainapp_corporateentity AS corporate_entity ON locale.corporateentity_id = corporate_entity.id
JOIN
    public.sustainapp_organization AS organization ON corporate_entity.organization_id = organization.id
JOIN
    public.datametric_emissionanalysis ON public.datametric_datapoint.raw_response_id = public.datametric_emissionanalysis.raw_response_id 
    AND public.datametric_datapoint.index = public.datametric_emissionanalysis.index
WHERE
    corporate_entity.client_id = public.datametric_datapoint.client_id
GROUP BY
    public.datametric_datapoint.index,
    public.datametric_datapoint.path_id,
    public.datametric_datapoint.raw_response_id,
    public.datametric_datapoint.month,
    public.datametric_datapoint.year,
    public.datametric_path.name,
    public.datametric_datapoint.locale_id,
    locale.name,
    corporate_entity.name,
    organization.name,
    public.datametric_datapoint.client_id,
    public.datametric_datapoint.user_id
ORDER BY
    public.datametric_datapoint.raw_response_id,
    public.datametric_datapoint.index;
"""


def updating_emission_data(raw_response: RawResponse):

    if "gri-environment-emissions-301-a-scope-" in raw_response.path.slug:
        with connection.cursor() as cursor:
            cursor.execute(SQL_SCRIPT)
        return "Successfully updated emission_data table"
