from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Location, Organization, Corporateentity
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from collections import defaultdict
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from django.db.models import Prefetch
from rest_framework import serializers


class GetMaterialAnalysis(APIView):

    def get_material_data(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Function to gather data from table renewable and non-renewable materials,
        it distinguish data by path slug send on function arguments"""
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__in=[start_year, end_year],
            month__in=[start_month, end_month],
            location__in=location,
        )

        renewable_materials_dict = defaultdict(
            lambda: {
                "material_type": "",
                "material_category": "",
                "source": "",
                "total_quantity": 0.0,
                "units": "",
                "data_source": "",
            }
        )

        for rw in raw_responses:
            for data in rw.data:
                material_type = data["Typeofmaterial"]
                material_category = data["Materialsused"]
                source = data["Source"]
                units = data["Unit"]
                data_source = data["Datasource"]
                total_quantity = float(data["Totalweight"])

                key = (material_type, material_category, source, units, data_source)

                renewable_materials_dict[key]["material_type"] = material_type
                renewable_materials_dict[key]["material_category"] = material_category
                renewable_materials_dict[key]["source"] = source
                renewable_materials_dict[key]["units"] = units
                renewable_materials_dict[key]["data_source"] = data_source
                renewable_materials_dict[key]["total_quantity"] += total_quantity

        renewable_materials = list(renewable_materials_dict.values())
        total_test = sum(
            item["total_quantity"] for item in renewable_materials_dict.values()
        )
        total_weight = {"total_weight": total_test}
        renewable_materials.append(total_weight)

        return renewable_materials

    def get_reclaimed_materials(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Funtion which will gather and structure data from table reclaimed materials,
        it distinguish data by path slug send on function arguments,
        it calcualte percentage of reclaimed products
        Field used to calculate:
        Total Amounts of product and packaging materials recycled(material_type) / Total Amount of products sold * 100
        """
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__in=[start_year, end_year],
            month__in=[start_month, end_month],
            location__in=location,
        )
        reclaimed_materials_dict = defaultdict(
            lambda: {
                "type_of_product": "",
                "product_code": "",
                "product_name": "",
                "total_quantity": 0.0,
                "percentage_of_reclaimed_products": "",
            }
        )
        total_product_packaging = 0.0
        for rw in raw_responses:
            for data in rw.data:
                type_of_product = data["Typesofproducts"]
                product_code = data["Productcode"]
                product_name = data["Productname"]
                total_quantity = float(data["Amountsproduct"])
                total_amount_of_product_packaging = float(data["Amountsproduct"])

                key = type_of_product

                reclaimed_materials_dict[key]["type_of_product"] = type_of_product
                reclaimed_materials_dict[key]["product_code"] = product_code
                reclaimed_materials_dict[key]["product_name"] = product_name
                reclaimed_materials_dict[key]["total_quantity"] += total_quantity
                total_product_packaging += total_amount_of_product_packaging

        for key, value in reclaimed_materials_dict.items():
            value["percentage_of_reclaimed_products"] = round(
                (value["total_quantity"] / total_product_packaging) * 100, 2
            )
        reclaimed_materials = list(reclaimed_materials_dict.values())
        return reclaimed_materials

    def get_recycled_materials(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Gathers and structure data for table recycled materials.
        Calculates percentage in the selected reporting period time
        Fields used to calculate percentage:
        Total Amount of recycled input material used / Total Amount of material recycled * 100
        """
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__in=[start_year, end_year],
            month__in=[start_month, end_month],
            location__in=location,
        )
        recycled_materials_dict = defaultdict(
            lambda: {
                "type_of_recycled_material_used": "",
                "total_recycled_input_materials_used": 0.0,
                "percentage_of_recycled_input_materials_used": 0.0,
            }
        )
        total_material_recycled = 0.0
        for rw in raw_responses:
            for data in rw.data:
                type_of_recycled_material = data["Typeofrecycledmaterialused"]
                recycled_input_material_used = float(
                    data["Amountofrecycledinputmaterialused"]
                )
                material_recycled = float(data["Amountofmaterialrecycled"])

                total_material_recycled += material_recycled

                key = type_of_recycled_material
                recycled_materials_dict[key][
                    "type_of_recycled_material_used"
                ] = type_of_recycled_material
                recycled_materials_dict[key][
                    "total_recycled_input_materials_used"
                ] += recycled_input_material_used

        for key, values in recycled_materials_dict.items():
            values["percentage_of_recycled_input_materials_used"] = round(
                (
                    values["total_recycled_input_materials_used"]
                    / total_material_recycled
                )
                * 100,
                2,
            )

        recycled_materials = list(recycled_materials_dict.values())
        return recycled_materials

    def get(self, request, format=None):

        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        self.organisation = serializer.validated_data.get("organisation", None)
        self.corporate = serializer.validated_data.get("corporate", None)
        self.location = serializer.validated_data.get("location", None)
        start = serializer.validated_data.get("start", None)
        end = serializer.validated_data.get("end", None)
        if self.organisation and self.corporate and self.location:
            self.locations = Location.objects.filter(id=self.location.id)
        elif (
            self.organisation is None and self.corporate and self.location is None
        ) or (self.organisation and self.corporate and self.location is None):
            self.locations = self.corporate.location.all()
        elif (
            self.organisation and self.corporate is None and self.location is None
        ) or (self.organisation is None and self.corporate and self.location):
            self.locations = Location.objects.prefetch_related(
                Prefetch(
                    "corporateentity",
                    queryset=self.organisation.corporatenetityorg.all(),
                )
            )
        else:
            raise serializers.ValidationError(
                "Not send any of the following fields: organisation, corporate, location"
            )
        location_names = self.locations.values_list("name", flat=True)

        renewable_materials = self.get_material_data(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-1a-renewable_materials",
        )

        non_renewable_materials = self.get_material_data(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-1a-non_renewable_materials",
        )

        recycled_materials = self.get_recycled_materials(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-2a-recycled_input_materials",
        )

        reclaimed_materials = self.get_reclaimed_materials(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-3a-3b-reclaimed_products",
        )

        return Response(
            {
                "renewable_materials": renewable_materials,
                "non_renewable_materials": non_renewable_materials,
                "recycled_materials": recycled_materials,
                "reclaimed_materials": reclaimed_materials,
            },
            status=status.HTTP_200_OK,
        )
