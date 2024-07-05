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


def get_integer(value):
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to an integer")
    else:
        raise TypeError(f"Expected int or str, got {type(value).__name__}")
    
def get_value(objectValue):
    if objectValue is None:
        return 0
    else:
        return objectValue

def safe_divide(numerator, denominator, decimal_places=2):
    return round((numerator / denominator * 100), decimal_places) if denominator != 0 else 0


class EmploymentAnalyzeView(APIView):
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
    employee_benefits_path_slugs = ["gri-social-benefits-401-2a-benefits_provided"]
    employee_parental_leave_path_slugs = ["gri-social-parental_leave-401-3a-3b-3c-3d-parental_leave"]

    new_employee_paths = {
        "permanent": new_employee_hire_path_slugs[0],
        "temporary": new_employee_hire_path_slugs[1],
        "nonguaranteed": new_employee_hire_path_slugs[2],
        "fulltime": new_employee_hire_path_slugs[3],
        "parttime": new_employee_hire_path_slugs[4]
    }
    employee_turnover_paths = {
        "permanent": employee_turnover_path_slugs[0],
        "temporary": employee_turnover_path_slugs[1],
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
        "entitlement_male": 0,
        "entitlement_female": 0,
        "entitlement_total": 0,
        "taking_male": 0,
        "taking_female": 0,
        "taking_total": 0,
        "return_to_post_work_male": 0,
        "return_to_post_work_female": 0,
        "return_to_post_work_total": 0,
        "retained_12_mts_male": 0,
        "retained_12_mts_female": 0,
        "retained_12_mts_total": 0,

    }

    def get_integer(value):
        if isinstance(value, int):
            return value
        elif isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to an integer")
        else:
            raise TypeError(f"Expected int or str, got {type(value).__name__}")

    def process_dataPoints(self, new_employ_dps, emp_turnover_dps, benefits_data_points,parental_leave_data_points):

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

        # new_employee_permanent

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

        print(ne_male_permanent_qs['number_holder__sum'])
        total_permanent = get_value(ne_male_permanent_qs['number_holder__sum']) + get_value(ne_female_permanent_qs['number_holder__sum']) + get_value(ne_nb_permanent_qs['number_holder__sum'])

        ne_per_male_percent = safe_divide(get_value(ne_male_permanent_qs['number_holder__sum']), total_permanent)
        ne_per_female_percent = safe_divide(get_value(ne_female_permanent_qs['number_holder__sum']), total_permanent)
        ne_per_nb_percent = safe_divide(get_value(ne_nb_permanent_qs['number_holder__sum']), total_permanent)
        ne_permanent_30_pc = safe_divide(get_value(ne_permanent_30_qs['number_holder__sum']), total_permanent)
        ne_permanent_30_50_pc = safe_divide(get_value(ne_permanent_30_50_qs['number_holder__sum']), total_permanent)
        ne_permanent_50_pc = safe_divide(get_value(ne_permanent_50_qs['number_holder__sum']), total_permanent)

        self.new_employee_reponse_table['new_employee_permanent_male_percent'] = ne_per_male_percent
        self.new_employee_reponse_table['new_employee_permanent_female_percent'] = ne_per_female_percent
        self.new_employee_reponse_table['new_employee_permanent_non_binary_percent'] = ne_per_nb_percent
        self.new_employee_reponse_table['new_employee_permanent_30_percent'] = ne_permanent_30_pc
        self.new_employee_reponse_table['new_employee_permanent_30-50_percent'] = ne_permanent_30_50_pc
        self.new_employee_reponse_table['new_employee_permanent_50_percent'] = ne_permanent_50_pc

        # new_employee temporary

        if dp_employ_temporary:
            dp_employ_temporary_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_temporary])
        else:
            dp_employ_temporary_qs = DataPoint.objects.none()  # Assuming DataPoint is your model


        ne_male_temporary_qs = dp_employ_temporary_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder')) 
        ne_female_temporary_qs = dp_employ_temporary_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        ne_nb_temporary_qs = dp_employ_temporary_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        ne_temporary_30_qs = dp_employ_temporary_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder')) 
        ne_temporary_30_50_qs = dp_employ_temporary_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder')) 
        ne_temporary_50_qs = dp_employ_temporary_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        print(ne_male_temporary_qs,ne_female_temporary_qs,ne_nb_temporary_qs)
            
        total_temporary = get_value(ne_male_temporary_qs['number_holder__sum']) + get_value( ne_female_temporary_qs['number_holder__sum'])  + get_value(ne_nb_temporary_qs['number_holder__sum'])
        
        ne_temp_male_percent = safe_divide(get_value( ne_male_temporary_qs['number_holder__sum'] ),total_temporary)
        ne_temp_female_percent = safe_divide( get_value(ne_female_temporary_qs['number_holder__sum']), total_temporary)
        ne_temp_nb_percent = safe_divide(get_value(ne_nb_temporary_qs['number_holder__sum']),total_temporary)
        ne_temp_30_pc = safe_divide( get_value( ne_temporary_30_qs['number_holder__sum']),total_temporary)
        ne_temp_30_50_pc = safe_divide(get_value(ne_temporary_30_50_qs['number_holder__sum']),total_temporary)
        ne_temp_50_pc = safe_divide(get_value( ne_temporary_50_qs['number_holder__sum']),total_temporary)

        self.new_employee_reponse_table['new_employee_temporary_male_percent'] = ne_temp_male_percent
        self.new_employee_reponse_table['new_employee_temporary_female_percent'] = ne_temp_female_percent
        self.new_employee_reponse_table['new_employee_temporary_non_binary_percent'] = ne_temp_nb_percent
        self.new_employee_reponse_table['new_employee_temporary_30_percent'] = ne_temp_30_pc
        self.new_employee_reponse_table['new_employee_temporary_30-50_percent'] = ne_temp_30_50_pc
        self.new_employee_reponse_table['new_employee_temporary_50_percent'] = ne_temp_50_pc

        # new_employee non guaranteed
        
        if dp_employ_non_guaranteed:
            dp_employ_non_guaranteed_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_non_guaranteed])
        else:
            dp_employ_non_guaranteed_qs = DataPoint.objects.none()  # Assuming DataPoint is your model


        ne_male_ng_qs = dp_employ_non_guaranteed_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        ne_female_ng_qs = dp_employ_non_guaranteed_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        ne_nb_ng_qs = dp_employ_non_guaranteed_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        ne_ng_30_qs = dp_employ_non_guaranteed_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        ne_ng_30_50_qs = dp_employ_non_guaranteed_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        ne_ng_50_qs = dp_employ_non_guaranteed_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        total_ng = get_value( ne_male_ng_qs['number_holder__sum'] )+ get_value(ne_female_ng_qs['number_holder__sum']) + get_value( ne_nb_ng_qs['number_holder__sum'])
        
        ne_ng_male_percent = safe_divide(get_value( ne_male_ng_qs['number_holder__sum']) ,total_ng)
        ne_ng_female_percent = safe_divide(get_value(ne_female_ng_qs['number_holder__sum']), total_ng)
        ne_ng_nb_percent = safe_divide(get_value(ne_nb_ng_qs['number_holder__sum']),total_ng)
        ne_ng_30_pc = safe_divide(get_value(ne_ng_30_qs['number_holder__sum']),total_ng)
        ne_ng_30_50_pc = safe_divide(get_value(ne_ng_30_50_qs['number_holder__sum']),total_ng)
        ne_ng_50_pc = safe_divide(get_value(ne_ng_50_qs['number_holder__sum']),total_ng)

        self.new_employee_reponse_table['new_employee_non_guaranteed_male_percent'] = ne_ng_male_percent
        self.new_employee_reponse_table['new_employee_non_guaranteed_female_percent'] = ne_ng_female_percent
        self.new_employee_reponse_table['new_employee_non_guaranteed_non_binary_percent'] = ne_ng_nb_percent
        self.new_employee_reponse_table['new_employee_non_guaranteed_30_percent'] = ne_ng_30_pc
        self.new_employee_reponse_table['new_employee_non_guaranteed_30-50_percent'] = ne_ng_30_50_pc
        self.new_employee_reponse_table['new_employee_non_guaranteed_50_percent'] = ne_ng_50_pc 

        # new_employee full time
        
        if dp_employ_full_time:
            dp_employ_full_time_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_full_time])
        else:
            dp_employ_full_time_qs = DataPoint.objects.none()  # Assuming DataPoint is your model


        ne_male_ft_qs = dp_employ_full_time_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        ne_female_ft_qs = dp_employ_full_time_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        ne_nb_ft_qs = dp_employ_full_time_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        ne_ft_30_qs = dp_employ_full_time_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        ne_ft_30_50_qs = dp_employ_full_time_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        ne_ft_50_qs = dp_employ_full_time_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        total_ft = get_value(ne_male_ft_qs['number_holder__sum']) + get_value(ne_female_ft_qs['number_holder__sum']) + get_value(ne_nb_ft_qs['number_holder__sum'])
        
        ne_ft_male_percent = safe_divide(get_value(ne_male_ft_qs['number_holder__sum']), total_ft)
        ne_ft_female_percent = safe_divide(get_value(ne_female_ft_qs['number_holder__sum']), total_ft)
        ne_ft_nb_percent = safe_divide(get_value(ne_nb_ft_qs['number_holder__sum']), total_ft)
        ne_ft_30_pc = safe_divide(get_value(ne_ft_30_qs['number_holder__sum']), total_ft)
        ne_ft_30_50_pc = safe_divide(get_value(ne_ft_30_50_qs['number_holder__sum']), total_ft)
        ne_ft_50_pc = safe_divide(get_value(ne_ft_50_qs['number_holder__sum']), total_ft)


        self.new_employee_reponse_table['new_employee_full_time_male_percent'] = ne_ft_male_percent
        self.new_employee_reponse_table['new_employee_full_time_female_percent'] = ne_ft_female_percent
        self.new_employee_reponse_table['new_employee_full_time_non_binary_percent'] = ne_ft_nb_percent
        self.new_employee_reponse_table['new_employee_full_time_30_percent'] = ne_ft_30_pc
        self.new_employee_reponse_table['new_employee_full_time_30-50_percent'] = ne_ft_30_50_pc
        self.new_employee_reponse_table['new_employee_full_time_50_percent'] = ne_ft_50_pc 
        
        # new_employee part time
        
        if dp_employ_part_time:
            dp_employ_part_time_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_part_time])
        else:
            dp_employ_part_time_qs = DataPoint.objects.none()  # Assuming DataPoint is your model


        ne_male_pt_qs = dp_employ_part_time_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        ne_female_pt_qs = dp_employ_part_time_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        ne_nb_pt_qs = dp_employ_part_time_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        ne_pt_30_qs = dp_employ_part_time_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        ne_pt_30_50_qs = dp_employ_part_time_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        ne_pt_50_qs = dp_employ_part_time_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        total_pt = get_value(ne_male_pt_qs['number_holder__sum']) + get_value(ne_female_pt_qs['number_holder__sum']) + get_value(ne_nb_pt_qs['number_holder__sum'])
        
        ne_pt_male_percent = safe_divide(get_value(ne_male_pt_qs['number_holder__sum']), total_pt)
        ne_pt_female_percent = safe_divide(get_value(ne_female_pt_qs['number_holder__sum']), total_pt)
        ne_pt_nb_percent = safe_divide(get_value(ne_nb_pt_qs['number_holder__sum']), total_pt)
        ne_pt_30_pc = safe_divide(get_value(ne_pt_30_qs['number_holder__sum']), total_pt)
        ne_pt_30_50_pc = safe_divide(get_value(ne_pt_30_50_qs['number_holder__sum']), total_pt)
        ne_pt_50_pc = safe_divide(get_value(ne_pt_50_qs['number_holder__sum']), total_pt)

        self.new_employee_reponse_table['new_employee_part_time_male_percent'] = ne_pt_male_percent
        self.new_employee_reponse_table['new_employee_part_time_female_percent'] = ne_pt_female_percent
        self.new_employee_reponse_table['new_employee_part_time_non_binary_percent'] = ne_pt_nb_percent
        self.new_employee_reponse_table['new_employee_part_time_30_percent'] = ne_pt_30_pc
        self.new_employee_reponse_table['new_employee_part_time_30-50_percent'] = ne_pt_30_50_pc
        self.new_employee_reponse_table['new_employee_part_time_50_percent'] = ne_pt_50_pc 


        # employee Turnover Response table

        dp_employ_to_full_time = []
        dp_employ_to_temporary = []
        dp_employ_to_non_guaranteed = []
        dp_employ_to_part_time = []
        dp_employ_to_permanent = []

        for dp in emp_turnover_dps:
            if(dp.path.slug == self.employee_turnover_paths['permanent']):
                dp_employ_to_permanent.append(dp)
            if(dp.path.slug == self.employee_turnover_paths['temporary']):
                dp_employ_to_temporary.append(dp)
            if(dp.path.slug == self.employee_turnover_paths['nonguaranteed']):
                dp_employ_to_non_guaranteed.append(dp)
            if(dp.path.slug == self.employee_turnover_paths['fulltime']):
                dp_employ_to_full_time.append(dp)
            if(dp.path.slug == self.employee_turnover_paths['parttime']):
                dp_employ_to_part_time.append(dp)

        # new_employee_turnover_permanent

        if dp_employ_to_permanent:
            dp_employ_to_permanent_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_to_permanent])
        else:
            dp_employ_to_permanent_qs = DataPoint.objects.none()  # Assuming DataPoint is your model

        
        et_male_permanent_qs = dp_employ_to_permanent_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        et_female_permanent_qs = dp_employ_to_permanent_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        et_nb_permanent_qs = dp_employ_to_permanent_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        et_permanent_30_qs = dp_employ_to_permanent_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        et_permanent_30_50_qs = dp_employ_to_permanent_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        et_permanent_50_qs = dp_employ_to_permanent_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        print(et_male_permanent_qs['number_holder__sum'])

        total_permanent_eto = get_value(et_male_permanent_qs['number_holder__sum']) + get_value(et_female_permanent_qs['number_holder__sum']) + get_value(et_nb_permanent_qs['number_holder__sum'])
        
        et_per_male_percent = safe_divide(get_value(et_male_permanent_qs['number_holder__sum']), total_permanent_eto)
        et_per_female_percent = safe_divide(get_value(et_female_permanent_qs['number_holder__sum']), total_permanent_eto)
        et_per_nb_percent = safe_divide(get_value(et_nb_permanent_qs['number_holder__sum']), total_permanent_eto)
        et_permanent_30_pc = safe_divide(get_value(et_permanent_30_qs['number_holder__sum']), total_permanent_eto)
        et_permanent_30_50_pc = safe_divide(get_value(et_permanent_30_50_qs['number_holder__sum']), total_permanent_eto)
        et_permanent_50_pc = safe_divide(get_value(et_permanent_50_qs['number_holder__sum']), total_permanent_eto)
        
        self.new_employee_reponse_table['employee_turnover_permanent_male_percent'] = et_per_male_percent
        self.new_employee_reponse_table['employee_turnover_permanent_female_percent'] = et_per_female_percent
        self.new_employee_reponse_table['employee_turnover_permanent_non_binary_percent'] = et_per_nb_percent
        self.new_employee_reponse_table['employee_turnover_permanent_30_percent'] = et_permanent_30_pc
        self.new_employee_reponse_table['employee_turnover_permanent_30-50_percent'] = et_permanent_30_50_pc
        self.new_employee_reponse_table['employee_turnover_permanent_50_percent'] = et_permanent_50_pc


        # new_employee_turnover_temporary

        if dp_employ_to_temporary:
            dp_employ_to_temporary_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_to_temporary])
        else:
            dp_employ_to_temporary_qs = DataPoint.objects.none()  # Assuming DataPoint is your model

        
        et_male_temporary_qs = dp_employ_to_temporary_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        et_female_temporary_qs = dp_employ_to_temporary_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        et_nb_temporary_qs = dp_employ_to_temporary_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        et_temporary_30_qs = dp_employ_to_temporary_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        et_temporary_30_50_qs = dp_employ_to_temporary_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        et_temporary_50_qs = dp_employ_to_temporary_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        print(et_temporary_30_qs['number_holder__sum'])

        total_temporary_eto = get_value(et_male_temporary_qs['number_holder__sum']) + get_value(et_female_temporary_qs['number_holder__sum']) + get_value(et_nb_temporary_qs['number_holder__sum'])        
        
        et_temp_male_percent = safe_divide(get_value(et_male_temporary_qs['number_holder__sum']), total_temporary_eto)
        et_temp_female_percent = safe_divide(get_value(et_female_temporary_qs['number_holder__sum']), total_temporary_eto)
        et_temp_nb_percent = safe_divide(get_value(et_nb_temporary_qs['number_holder__sum']), total_temporary_eto)
        et_temp_30_pc = safe_divide(get_value(et_temporary_30_qs['number_holder__sum']), total_temporary_eto)
        et_temp_30_50_pc = safe_divide(get_value(et_temporary_30_50_qs['number_holder__sum']), total_temporary_eto)
        et_temp_50_pc = safe_divide(get_value(et_temporary_50_qs['number_holder__sum']), total_temporary_eto)
        
        self.new_employee_reponse_table['employee_turnover_temporary_male_percent'] = et_temp_male_percent
        self.new_employee_reponse_table['employee_turnover_temporary_female_percent'] = et_temp_female_percent
        self.new_employee_reponse_table['employee_turnover_temporary_non_binary_percent'] = et_temp_nb_percent
        self.new_employee_reponse_table['employee_turnover_temporary_30_percent'] = et_temp_30_pc
        self.new_employee_reponse_table['employee_turnover_temporary_30-50_percent'] = et_temp_30_50_pc
        self.new_employee_reponse_table['employee_turnover_temporary_50_percent'] = et_temp_50_pc

        # new_employee_turover _non guaranteed

        if dp_employ_to_non_guaranteed:
            dp_employ_to_ng_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_to_non_guaranteed])
        else:
            dp_employ_to_ng_qs = DataPoint.objects.none()  # Assuming DataPoint is your model

        
        et_male_ng_qs = dp_employ_to_ng_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        et_female_ng_qs = dp_employ_to_ng_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        et_nb_ng_qs = dp_employ_to_ng_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        et_ng_30_qs = dp_employ_to_ng_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        et_ng_30_50_qs = dp_employ_to_ng_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        et_ng_50_qs = dp_employ_to_ng_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        print(et_male_ng_qs['number_holder__sum'])

        total_ng_eto = get_value(et_male_ng_qs['number_holder__sum']) + get_value(et_female_ng_qs['number_holder__sum']) + get_value(et_nb_ng_qs['number_holder__sum'])

        et_ng_male_percent = safe_divide(get_value(et_male_ng_qs['number_holder__sum']), total_ng_eto)
        et_ng_female_percent = safe_divide(get_value(et_female_ng_qs['number_holder__sum']), total_ng_eto)
        et_ng_nb_percent = safe_divide(get_value(et_nb_ng_qs['number_holder__sum']), total_ng_eto)
        et_ng_30_pc = safe_divide(get_value(et_ng_30_qs['number_holder__sum']), total_ng_eto)
        et_ng_30_50_pc = safe_divide(get_value(et_ng_30_50_qs['number_holder__sum']), total_ng_eto)
        et_ng_50_pc = safe_divide(get_value(et_ng_50_qs['number_holder__sum']), total_ng_eto)
        
        self.new_employee_reponse_table['employee_turnover_non_guaranteed_male_percent'] = et_ng_male_percent
        self.new_employee_reponse_table['employee_turnover_non_guaranteed_female_percent'] = et_ng_female_percent
        self.new_employee_reponse_table['employee_turnover_non_guaranteed_non_binary_percent'] = et_ng_nb_percent
        self.new_employee_reponse_table['employee_turnover_non_guaranteed_30_percent'] = et_ng_30_pc
        self.new_employee_reponse_table['employee_turnover_non_guaranteed_30-50_percent'] = et_ng_30_50_pc
        self.new_employee_reponse_table['employee_turnover_non_guaranteed_50_percent'] = et_ng_50_pc

        # new_employee_turover _full_time

        if dp_employ_to_full_time:
            dp_employ_to_ft_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_to_full_time])
        else:
            dp_employ_to_ft_qs = DataPoint.objects.none()  # Assuming DataPoint is your model

        
        et_male_ft_qs = dp_employ_to_ft_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        et_female_ft_qs = dp_employ_to_ft_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        et_nb_ft_qs = dp_employ_to_ft_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        et_ft_30_qs = dp_employ_to_ft_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        et_ft_30_50_qs = dp_employ_to_ft_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        et_ft_50_qs = dp_employ_to_ft_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        print(et_male_ft_qs['number_holder__sum'])

        total_ft_eto = get_value(et_male_ft_qs['number_holder__sum']) + get_value(et_female_ft_qs['number_holder__sum']) + get_value(et_nb_ft_qs['number_holder__sum'])

        et_ft_male_percent = safe_divide(get_value(et_male_ft_qs['number_holder__sum']), total_ft_eto)
        et_ft_female_percent = safe_divide(get_value(et_female_ft_qs['number_holder__sum']), total_ft_eto)
        et_ft_nb_percent = safe_divide(get_value(et_nb_ft_qs['number_holder__sum']), total_ft_eto)
        et_ft_30_pc = safe_divide(get_value(et_ft_30_qs['number_holder__sum']), total_ft_eto)
        et_ft_30_50_pc = safe_divide(get_value(et_ft_30_50_qs['number_holder__sum']), total_ft_eto)
        et_ft_50_pc = safe_divide(get_value(et_ft_50_qs['number_holder__sum']), total_ft_eto)
        
        self.new_employee_reponse_table['employee_turnover_full_time_male_percent'] = et_ft_male_percent
        self.new_employee_reponse_table['employee_turnover_full_time_female_percent'] = et_ft_female_percent
        self.new_employee_reponse_table['employee_turnover_full_time_non_binary_percent'] = et_ft_nb_percent
        self.new_employee_reponse_table['employee_turnover_full_time_30_percent'] = et_ft_30_pc
        self.new_employee_reponse_table['employee_turnover_full_time_30-50_percent'] = et_ft_30_50_pc
        self.new_employee_reponse_table['employee_turnover_full_time_50_percent'] = et_ft_50_pc

        # new_employee_turover _parttime

        if dp_employ_to_part_time:
            dp_employ_to_pt_qs = DataPoint.objects.filter(id__in=[dp.id for dp in dp_employ_to_part_time])
        else:
            dp_employ_to_pt_qs = DataPoint.objects.none()  # Assuming DataPoint is your model

        
        et_male_pt_qs = dp_employ_to_pt_qs.filter(index=0, metric_name='total').aggregate(Sum('number_holder'))
        et_female_pt_qs = dp_employ_to_pt_qs.filter(index=1, metric_name='total').aggregate(Sum('number_holder'))
        et_nb_pt_qs = dp_employ_to_pt_qs.filter(index=2, metric_name='total').aggregate(Sum('number_holder'))

        et_pt_30_qs = dp_employ_to_pt_qs.filter(metric_name='yearsold30').aggregate(Sum('number_holder'))
        et_pt_30_50_qs = dp_employ_to_pt_qs.filter(metric_name='yearsold30to50').aggregate(Sum('number_holder'))
        et_pt_50_qs = dp_employ_to_pt_qs.filter(metric_name='yearsold50').aggregate(Sum('number_holder'))

        print(et_male_pt_qs['number_holder__sum'])

        total_pt_eto = get_value(et_male_pt_qs['number_holder__sum']) + get_value(et_female_pt_qs['number_holder__sum']) + get_value(et_nb_pt_qs['number_holder__sum'])

        et_pt_male_percent = safe_divide(get_value(et_male_pt_qs['number_holder__sum']), total_pt_eto)
        et_pt_female_percent = safe_divide(get_value(et_female_pt_qs['number_holder__sum']), total_pt_eto)
        et_pt_nb_percent = safe_divide(get_value(et_nb_pt_qs['number_holder__sum']), total_pt_eto)
        et_pt_30_pc = safe_divide(get_value(et_pt_30_qs['number_holder__sum']), total_pt_eto)
        et_pt_30_50_pc = safe_divide(get_value(et_pt_30_50_qs['number_holder__sum']), total_pt_eto)
        et_pt_50_pc = safe_divide(get_value(et_pt_50_qs['number_holder__sum']), total_pt_eto)
        
        self.new_employee_reponse_table['employee_turnover_part_time_male_percent'] = et_pt_male_percent
        self.new_employee_reponse_table['employee_turnover_part_time_female_percent'] = et_pt_female_percent
        self.new_employee_reponse_table['employee_turnover_part_time_non_binary_percent'] = et_pt_nb_percent
        self.new_employee_reponse_table['employee_turnover_part_time_30_percent'] = et_pt_30_pc
        self.new_employee_reponse_table['employee_turnover_part_time_30-50_percent'] = et_pt_30_50_pc
        self.new_employee_reponse_table['employee_turnover_part_time_50_percent'] = et_pt_50_pc

        benefits_dps = benefits_data_points
        parental_leave_dps = parental_leave_data_points

        # parental leave first

        self.parental_leave_response_table['entitlement_male'] = get_integer(get_value(parental_leave_data_points.filter(index=0, metric_name="male").first().value))
        self.parental_leave_response_table['entitlement_female'] = get_integer(get_value(parental_leave_data_points.filter(index=0, metric_name="female").first().value))
        self.parental_leave_response_table['entitlement_total'] = self.parental_leave_response_table['entitlement_male'] + self.parental_leave_response_table['entitlement_female']

        self.parental_leave_response_table['taking_male'] = get_integer(get_value(parental_leave_data_points.filter(index=1, metric_name="male").first().value))
        self.parental_leave_response_table['taking_female'] = get_integer(get_value(parental_leave_data_points.filter(index=1, metric_name="female").first().value))
        self.parental_leave_response_table['taking_total'] = self.parental_leave_response_table['taking_male'] + self.parental_leave_response_table['taking_female']
        
        self.parental_leave_response_table['return_to_post_work_male'] = get_integer(get_value(parental_leave_data_points.filter(index=2, metric_name="male").first().value))
        self.parental_leave_response_table['return_to_post_work_female'] = get_integer(get_value(parental_leave_data_points.filter(index=2, metric_name="female").first().value))
        self.parental_leave_response_table['return_to_post_work_total'] = self.parental_leave_response_table['return_to_post_work_male'] + self.parental_leave_response_table['return_to_post_work_female']

        self.parental_leave_response_table['retained_12_mts_male'] = get_integer(get_value(parental_leave_data_points.filter(index=3, metric_name="male").first().value))
        self.parental_leave_response_table['retained_12_mts_female'] = get_integer(get_value(parental_leave_data_points.filter(index=3, metric_name="female").first().value))
        self.parental_leave_response_table['retained_12_mts_total'] = self.parental_leave_response_table['retained_12_mts_male'] + self.parental_leave_response_table['retained_12_mts_female']

        # benefits table

        self.benefits_response_table['life_insurance_full_time'] = benefits_dps.filter(index=0,metric_name="fulltime").first().value
        self.benefits_response_table['life_insurance_part_time'] = benefits_dps.filter(index=0,metric_name="parttime").first().value
        self.benefits_response_table['life_insurance_temporary'] = benefits_dps.filter(index=0,metric_name="temporary").first().value

        self.benefits_response_table['healthcare_full_time'] = benefits_dps.filter(index=1,metric_name="fulltime").first().value
        self.benefits_response_table['healthcare_part_time'] = benefits_dps.filter(index=1,metric_name="parttime").first().value
        self.benefits_response_table['healthcare_temporary'] = benefits_dps.filter(index=1,metric_name="temporary").first().value

        self.benefits_response_table['disability_cover_full_time'] = benefits_dps.filter(index=2,metric_name="fulltime").first().value
        self.benefits_response_table['disability_cover_part_time'] = benefits_dps.filter(index=2,metric_name="parttime").first().value
        self.benefits_response_table['disability_cover_temporary'] = benefits_dps.filter(index=2,metric_name="temporary").first().value

        self.benefits_response_table['parental_leave_full_time'] = benefits_dps.filter(index=3,metric_name="fulltime").first().value
        self.benefits_response_table['parental_leave_part_time'] = benefits_dps.filter(index=3,metric_name="parttime").first().value
        self.benefits_response_table['parental_leave_temporary'] = benefits_dps.filter(index=3,metric_name="temporary").first().value

        self.benefits_response_table['retirement_full_time'] = benefits_dps.filter(index=4,metric_name="fulltime").first().value
        self.benefits_response_table['retirement_part_time'] = benefits_dps.filter(index=4,metric_name="parttime").first().value
        self.benefits_response_table['retirement_temporary'] = benefits_dps.filter(index=4,metric_name="temporary").first().value
  
        self.benefits_response_table['stock_ownership_full_time'] = benefits_dps.filter(index=5,metric_name="fulltime").first().value
        self.benefits_response_table['stock_ownership_part_time'] = benefits_dps.filter(index=5,metric_name="parttime").first().value
        self.benefits_response_table['stock_ownership_temporary'] = benefits_dps.filter(index=5,metric_name="temporary").first().value

        


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
        benefits_data_points = DataPoint.objects.filter(client_id=client_id,path__slug__in = self.employee_benefits_path_slugs, year=2024, location='Loc Yash', month=1)
        parental_leave_data_points = DataPoint.objects.filter(client_id=client_id,path__slug__in = self.employee_parental_leave_path_slugs, year=2024, location='Loc Yash', month=1)
        
        # pushing for processing
        self.process_dataPoints(new_emp_data_points, emp_turnover_data_points, benefits_data_points, parental_leave_data_points)
        # * Get top emissions by Scope
        response_data = dict()
        response_data['success_true'] = 'true'
        response_data['new_employee_response_table'] = self.new_employee_reponse_table
        response_data['employee_turnover_reponse_table'] = self.employee_turnover_reponse_table
        response_data['benefits_response_table'] = self.benefits_response_table
        response_data['parental_leave_response_table'] = self.parental_leave_response_table

        return Response({"data": response_data}, status=status.HTTP_200_OK)
