from datametric.models import DataPoint, Path, DataMetric, RawResponse
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import set_locations_data
from operator import itemgetter

from django.db.models import Prefetch
from rest_framework import serializers
from django.db.models import QuerySet
from django.db.models import Sum


class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]
    new_employee_hire_path_slugs = [
            "gri-social-employee_hires-401-1a-new_emp_hire-permanent_emp",
            "gri-social-employee_hires-401-1a-new_emp_hire-temp_emp",
            "gri-social-employee_hires-401-1a-new_emp_hire-nongauranteed",
            "gri-social-employee_hires-401-1a-new_emp_hire-fulltime",
            "gri-social-employee_hires-401-1a-new_emp_hire-parttime",
        ]
    employee_turnover_path_slugs = [
            "gri-social-employee_hires-401-1a-emp_turnover-permanent_emp",
            "gri-social-employee_hires-401-1a-emp_turnover-temp_emp",
            "gri-social-employee_hires-401-1a-emp_turnover-nonguaranteed",
            "gri-social-employee_hires-401-1a-emp_turnover-fulltime",
            "gri-social-employee_hires-401-1a-emp_turnover-parttime",
        ]
    new_employee_paths = {
        "permanent": new_employee_hire_path_slugs[0],
        "temporary": new_employee_hire_path_slugs[1],
        "nonguaranteed": new_employee_hire_path_slugs[2],
        "fulltime": new_employee_hire_path_slugs[3],
        "parttime": new_employee_hire_path_slugs[4]
    }
    employee_turnover_paths = {
        "permanent": employee_turnover_path_slugs[0],
        "temp_emp": employee_turnover_path_slugs[1],
        "nonguaranteed": employee_turnover_path_slugs[2],
        "fulltime": employee_turnover_path_slugs[3],
        "parttime": employee_turnover_path_slugs[4]
    }
    metric_names_new_employee = {
        "30": "yearsold30",
        "30-50": "yearsold30-50",
        "50": "yearsold50",
        "total": "total",
    }
    metric_names_employeeTurnover = {
        "30": "yearsold30",
        "30-50": "yearsold30-50",
        "50": "yearsold50",
        "end": "end",
        "beginning": "beginning"
    }
    new_employee_reponse_table = {
        # permanent
        "new_employee_permanent_male_percent": 0,
        "new_employee_permanent_female_percent": 0,
        "new_employee_permanent_non_binary_percent":0,
        "new_employee_permanent_30_percent":0,
        "new_employee_permanent_30-50_percent":0,
        "new_employee_permanent_50_percent":0,
        # temporary
        "new_employee_temporary_male_percent": 0,
        "new_employee_temporary_female_percent": 0,
        "new_employee_temporary_non_binary_percent":0,
        "new_employee_temporary_30_percent":0,
        "new_employee_temporary_30-50_percent":0,
        "new_employee_temporary_50_percent":0,
        # non guaranteed
        "new_employee_non_guaranteed_male_percent": 0,
        "new_employee_non_guaranteed_female_percent": 0,
        "new_employee_non_guaranteed_non_binary_percent":0,
        "new_employee_non_guaranteed_30_percent":0,
        "new_employee_non_guaranteed_30-50_percent":0,
        "new_employee_non_guaranteed_50_percent":0,
        # full time
        "new_employee_full_time_male_percent": 0,
        "new_employee_full_time_female_percent": 0,
        "new_employee_full_time_non_binary_percent":0,
        "new_employee_full_time_30_percent":0,
        "new_employee_full_time_30-50_percent":0,
        "new_employee_full_time_50_percent":0,
        # part time
        "new_employee_part_time_male_percent": 0,
        "new_employee_part_time_female_percent": 0,
        "new_employee_part_time_non_binary_percent":0,
        "new_employee_part_time_30_percent":0,
        "new_employee_part_time_30-50_percent":0,
        "new_employee_part_time_50_percent":0,
    }
    employee_turnover_reponse_table = {
        # permanent
        "employee_turnover_permanent_male_percent": 0,
        "employee_turnover_permanent_female_percent": 0,
        "employee_turnover_permanent_non_binary_percent":0,
        "employee_turnover_permanent_30_percent":0,
        "employee_turnover_permanent_30-50_percent":0,
        "employee_turnover_permanent_50_percent":0,
        # temporary_turnover
        "employee_turnover_temporary_male_percent": 0,
        "employee_turnover_temporary_female_percent": 0,
        "employee_turnover_temporary_non_binary_percent":0,
        "employee_turnover_temporary_30_percent":0,
        "employee_turnover_temporary_30-50_percent":0,
        "employee_turnover_temporary_50_percent":0,
        # guaranteed_turnover
        "employee_turnover_non_guaranteed_male_percent": 0,
        "employee_turnover_non_guaranteed_female_percent": 0,
        "employee_turnover_non_guaranteed_non_binary_percent":0,
        "employee_turnover_non_guaranteed_30_percent":0,
        "employee_turnover_non_guaranteed_30-50_percent":0,
        "employee_turnover_non_guaranteed_50_percent":0,
        # fulltime_turnover
        "employee_turnover_full_time_male_percent": 0,
        "employee_turnover_full_time_female_percent": 0,
        "employee_turnover_full_time_non_binary_percent":0,
        "employee_turnover_full_time_30_percent":0,
        "employee_turnover_full_time_30-50_percent":0,
        "employee_turnover_full_time_50_percent":0,
        # parttime_turnover
        "employee_turnover_part_time_male_percent": 0,
        "employee_turnover_part_time_female_percent": 0,
        "employee_turnover_part_time_non_binary_percent":0,
        "employee_turnover_part_time_30_percent":0,
        "employee_turnover_part_time_30-50_percent":0,
        "employee_turnover_part_time_50_percent":0,
    }

    benefits_response_table = {
        # "life insurance, healthcare, disability_cover, parental_leave, retirement, stock_ownership",
        # "fulltime, partime, temporary"
        "life_insurance_full_time": True,
        "life_insurance_part_time": True,
        "life_insurance_temporary": True,
        "healthcare_full_time": True,
        "healthcare_part_time": True,
        "healthcare_temporary": True,
        "disability_cover_full_time": True,
        "disability_cover_part_time": True,
        "disability_cover_temporary": True,
        "parental_leave_full_time": True,
        "parental_leave_part_time": True,
        "parental_leave_temporary": True,
        "retirement_full_time": True,
        "retirement_part_time": True,
        "retirement_temporary": True,
        "stock_ownership_full_time": True,
        "stock_ownership_part_time": True,
        "stock_ownership_temporary": True,
    }
    parental_leave_response_table = {
        # "life insurance, healthcare, disability_cover, parental_leave, retirement, stock_ownership",
        # "fulltime, partime, temporary"
        "entitlement_full_time": True,
        "entitlement_part_time": True,
        "entitlement_temporary_time": True,
        "taking_full_time": True,
        "taking_part_time": True,
        "taking_temporary": True,
        "return_to_post_work_full_time": True,
        "return_to_post_work_part_time": True,
        "return_to_post_work_temporary": True,
        "retained_12_mts_full_time": True,
        "retained_12_mts_part_time": True,
        "retained_12_mts_temporary": True,
        "return_to_work_full_time": True,
        "return_to_work_part_time": True,
        "return_to_work_temporary": True,
        "retention_rate_full_time": True,
        "retention_rate_part_time": True,
        "retention_rate_temporary": True,
    }

    def process_dataPoints(self, new_employ_dps, emp_turnover_dps):

        print('new employ dps *****')
        dp_employ_permanent = []
        dp_employ_permanent_qs = []

        dp_employ_full_time = []
        dp_employ_temporary = []
        dp_employ_non_guaranteed = []
        dp_employ_part_time = []
        dp_employ_permanent_qs = []
        total_new_employs = len(new_employ_dps)

        for dp in new_employ_dps:
            if(dp.path.slug == self.new_employee_paths['permanent']):
                dp_employ_permanent.append(dp)
            if(dp.path.slug == self.new_employee_paths['temporary']):
                dp_employ_temporary.append(dp)
            if(dp.path.slug == self.new_employee_paths['nonguaranteed']):
                dp_employ_non_guaranteed.append(dp)
            if(dp.path.slug == self.new_employee_paths['fulltime']):
                dp_employ_full_time.append(dp)
            if(dp.path.slug == self.new_employee_paths['parttime']):
                dp_employ_part_time.append(dp)
            # male, female, non-binary ==> index; 30,30-50, 50 is metric_name

        if dp_employ_permanent:
            dp_employ_permanent_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_permanent])
        else:
            dp_employ_permanent_qs = DataPoint.objects.none()  # Assuming DataPoint is your model

        ne_male_permanent_qs = dp_employ_permanent_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        ne_female_permanent_qs = dp_employ_permanent_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        ne_nb_permanent_qs = dp_employ_permanent_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        ne_permanent_30_qs = dp_employ_permanent_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        ne_permanent_30_50_qs = dp_employ_permanent_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        ne_permanent_50_qs = dp_employ_permanent_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        # total_employee_permanent = ne_male_permanent_qs['number_holder__Sum'] 
        # print(total_employee_permanent)
        print(ne_male_permanent_qs['number_holder__sum'])
        total_permanent = ne_male_permanent_qs['number_holder__sum'] + ne_female_permanent_qs['number_holder__sum'] + ne_nb_permanent_qs['number_holder__sum']
        ne_per_male_percent = round((ne_male_permanent_qs['number_holder__sum'] / total_permanent * 100),2)
        ne_per_female_percent = round((ne_female_permanent_qs['number_holder__sum']/ total_permanent * 100),2)
        ne_per_nb_percent = round((ne_nb_permanent_qs['number_holder__sum']/total_permanent * 100),2)
        ne_permanent_30_pc = round((ne_permanent_30_qs['number_holder__sum']/total_permanent * 100),2)
        ne_permanent_30_50_pc = round((ne_permanent_30_50_qs['number_holder__sum']/total_permanent * 100),2)
        ne_permanent_50_pc = round((ne_permanent_50_qs['number_holder__sum']/total_permanent * 100),2)

        

        
        # 


        # for dp in emp_turnover_dps:
        #     print(dp.id, ' - ', dp.metric_name)


    def get(self, request, format=None):
        """
        Returns a dictionary with keys containing
        1. Top Emission by Scope
        2. Top Emission by Source
        3. Top Emission by Location
        filtered by Organisation, Corporate and Year"""

        # * Get all the RawResponses
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.corporate = serializer.validated_data.get(
            "corporate"
        )  # * This is optional
        self.organisation = serializer.validated_data["organisation"]
        self.location = serializer.validated_data.get("location")  # * This is optional
        # * Set Locations Queryset
        self.locations = set_locations_data(
            organisation=self.organisation,
            corporate=self.corporate,
            location=self.location,
        )
        client_id = request.user.client.id
        new_emp_data_points = DataPoint.objects.filter(client_id=client_id, path__slug__in = self.new_employee_hire_path_slugs, year=2024,location='Loc Yash',month=1)
        emp_turnover_data_points = DataPoint.objects.filter(client_id=client_id, path__slug__in = self.employee_turnover_path_slugs,year=2024,location='Loc Yash',month=1)

        self.process_dataPoints(new_emp_data_points, emp_turnover_data_points)
        # * Get top emissions by Scope
        response_data = dict()
        response_data['success_true'] = 'true'
        return Response({"data": response_data}, status=status.HTTP_200_OK)
