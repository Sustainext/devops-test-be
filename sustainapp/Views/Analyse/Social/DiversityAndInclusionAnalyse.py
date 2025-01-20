from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
    safe_divide_percentage,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_segregated_by_location,
    collect_data_by_raw_response_and_index,
)
from datametric.models import RawResponse, DataPoint
from sustainapp.models import Corporateentity
from common.utils.value_types import safe_divide
from logging import getLogger

logger = getLogger("error.log")


class DiversityAndInclusionAnalyse(APIView):
    permission_classes = [IsAuthenticated]

    slugs = [
        "gri-social-diversity_of_board-405-1a-number_of_individuals",
        "gri-social-salary_ratio-405-2a-number_of_individuals",
        "gri-social-salary_ratio-405-2a-ratio_of_remuneration",
    ]

    def set_raw_responses(self):
        user = self.request.user
        self.raw_response = (
            RawResponse.objects.filter(
                path__slug__in=self.slugs,
                client=user.client,
            )
            .filter(year__range=(self.start.year, self.end.year))
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .prefetch_related("path")
            .order_by("-year", "-month")
        )

    def set_data_points(self):
        client_id = self.request.user.client.id
        self.data_points = (
            DataPoint.objects.filter(
                client_id=client_id,
                path__slug__in=self.slugs,
            )
            .filter(filter_by_start_end_dates(self.start, self.end))
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
        )

    def get_diversity_of_the_individuals(self, slug):
        """
        Gets data by location and then calculates the percentage of the total of each point within the location data.
        """
        data_points = self.data_points.filter(path__slug=slug).order_by("index")
        location_wise_data = collect_data_segregated_by_location(data_points)
        response_data = []
        for data in location_wise_data:
            response_dict = {}
            for item in data:
                for key, value in item.items():
                    if key != "category":
                        if key in response_dict:
                            response_dict[key] += int(value)
                        else:
                            response_dict[key] = int(value)
            calculation_dict = {
                "male_percentage": 0,
                "female_percentage": 0,
                "nonBinary_percentage": 0,
                "lessThan30_percentage": 0,
                "between30and50_percentage": 0,
                "moreThan50_percentage": 0,
                "minorityGroup_percentage": 0,
                "vulnerableCommunities_percentage": 0,
            }
            # Calculating percentages
            if response_dict["totalGender"] > 0:
                calculation_dict["male_percentage"] = safe_divide_percentage(
                    response_dict["male"], response_dict["totalGender"]
                )
                calculation_dict["female_percentage"] = safe_divide_percentage(
                    response_dict["female"], response_dict["totalGender"]
                )
                calculation_dict["nonBinary_percentage"] = safe_divide_percentage(
                    response_dict["nonBinary"], response_dict["totalGender"]
                )

            if response_dict["totalAge"] > 0:
                calculation_dict["lessThan30_percentage"] = safe_divide_percentage(
                    response_dict["lessThan30"], response_dict["totalAge"]
                )
                calculation_dict["between30and50_percentage"] = safe_divide_percentage(
                    response_dict["between30and50"], response_dict["totalAge"]
                )
                calculation_dict["moreThan50_percentage"] = safe_divide_percentage(
                    response_dict["moreThan50"],
                    response_dict["totalAge"],
                )

            # Calculating minority group percentage
            total_minority_and_vulnerable = (
                response_dict["minorityGroup"] + response_dict["vulnerableCommunities"]
            )
            if total_minority_and_vulnerable > 0:
                calculation_dict["minorityGroup_percentage"] = safe_divide_percentage(
                    response_dict["minorityGroup"], total_minority_and_vulnerable
                )
                calculation_dict["vulnerableCommunities_percentage"] = (
                    safe_divide_percentage(
                        response_dict["vulnerableCommunities"],
                        total_minority_and_vulnerable,
                    )
                )
            response_data.append(response_dict)
        return response_data

    def get_salary_ration(self, slug):  # 405-2
        dps = self.data_points.filter(path__slug=slug).order_by("index")
        data = collect_data_by_raw_response_and_index(dps)
        response_data = []
        # response_data.append({
        #     "Q2":[]
        #     "Q1":
        # })

    def format_data(self, raw_resp_1a, currency: float) -> list:
        # What if they don't add the values in male and female
        res = []
        for obj in raw_resp_1a.data[0]["Q4"]:
            try:
                obj["Male"] = safe_divide((obj["Male"]), currency)
                obj["Female"] = safe_divide((obj["Female"]), currency)
                obj["Non-binary"] = safe_divide((obj["Non-binary"]), currency)
                res.append(obj)
            except Exception as e:
                logger.error(f"Analyze Economic Market Precesnse error : {e}")
                continue

        return res

    def process_market_presence(self, path, filter_by):
        raw_resp_1a = (
            RawResponse.objects.filter(
                **filter_by,
                path__slug=path,
                client_id=self.client_id,
                year__range=(self.start.year, self.end.year),
            )
            .order_by("-year")
            .first()
        )

        raw_resp_1c = (
            RawResponse.objects.filter(
                **filter_by,
                path__slug="gri-economic-ratios_of_standard_entry-202-1c-location",
                client_id=self.client_id,
                year__range=(self.start.year, self.end.year),
            )
            .order_by("-year")
            .first()
        )
        if raw_resp_1a and raw_resp_1c:
            if (
                raw_resp_1a.data[0]["Q4"]
                and raw_resp_1a.data[0]["Q3"]
                == raw_resp_1c.data[0]["Currency"].split(" ")[1]
            ):
                currency = float(raw_resp_1c.data[0]["Currency"].split(" ")[0])
                return self.format_data(raw_resp_1a, currency)
            else:
                raise KeyError("Please add data and also match the currency")

        elif not raw_resp_1a and not raw_resp_1c and self.corporate is None:
            logger.error(
                f"Economic/MarketPresenceAnalyse : There is no data for the organization {self.organisation} and the path {path} and the year between {self.start.year} and {self.end.year}, So proceeding to check for its Corporates"
            )
            corps_of_org = Corporateentity.objects.filter(
                organization__id=self.organisation.id
            )
            corp_res = []
            for corp in corps_of_org:
                raw_resp_1a = (
                    RawResponse.objects.filter(
                        organization__id=self.organisation.id,
                        corporate__id=corp.id,
                        path__slug=path,
                        client_id=self.client_id,
                        year__range=(self.start.year, self.end.year),
                    )
                    .order_by("-year")
                    .first()
                )
                raw_resp_1c = (
                    RawResponse.objects.filter(
                        organization__id=self.organisation.id,
                        corporate__id=corp.id,
                        path__slug="gri-economic-ratios_of_standard_entry-202-1c-location",
                        client_id=self.client_id,
                        year__range=(self.start.year, self.end.year),
                    )
                    .order_by("-year")
                    .first()
                )

                if raw_resp_1a and raw_resp_1c:
                    corp_res.extend(
                        self.format_data(
                            raw_resp_1a,
                            float(raw_resp_1c.data[0]["Currency"].split(" ")[0]),
                        )
                    )

            return corp_res

        else:
            # There is no data added
            return []

    def get(self, request):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.set_raw_responses()
        self.set_data_points()
        self.client_id = request.user.client.id

        filter_by = {}

        filter_by["organization__id"] = self.organisation.id

        if self.corporate is not None:
            filter_by["corporate__id"] = self.corporate.id
        else:
            filter_by["corporate__id"] = None

        marketing_presence_ratio = self.process_market_presence(
            "gri-economic-ratios_of_standard_entry_level_wage_by_gender_compared_to_local_minimum_wage-202-1a-s1",
            filter_by,
        )
        response_data = {
            "percentage_of_employees_within_government_bodies": self.get_diversity_of_the_individuals(
                self.slugs[0]
            ),
            "ratio_of_basic_salary_of_women_to_men": self.get_salary_ration(
                self.slugs[1]
            ),
            "ratio_of_remuneration_of_women_to_men": self.get_salary_ration(
                self.slugs[2]
            ),
            "marketing_presence": marketing_presence_ratio,
        }

        return Response(response_data, status=status.HTTP_200_OK)
