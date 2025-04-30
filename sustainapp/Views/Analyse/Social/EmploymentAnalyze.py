import logging
from datetime import datetime
from django.db.models import Q, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datametric.models import DataPoint
from datametric.utils.analyse import safe_divide_percentage, get_raw_response_filters,filter_by_start_end_dates
from common.utils.get_data_points_as_raw_responses import collect_data_by_raw_response_and_index
from sustainapp.models import Organization, Corporateentity, Location
import math 

logger = logging.getLogger("emp_nvn")

def format_float(val):
    try:
        return f"{float(val):.2f}"
    except (ValueError, TypeError):
        return "0.00"


class EmploymentAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    new_employee_hire_path_slugs = [
        "gri-social-employee_hires-401-1a-new_emp_hire-permanent_emp",
        "gri-social-employee_hires-401-1a-new_emp_hire-temp_emp",
        "gri-social-employee_hires-401-1a-new_emp_hire-nonguaranteed",
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
    employee_benefits_path_slugs = [
        "gri-social-benefits-401-2a-benefits_provided",
        "gri-social-benefits-401-2a-benefits_provided_tab_1",
        "gri-social-benefits-401-2a-benefits_provided_tab_2",
        "gri-social-benefits-401-2a-benefits_provided_tab_3",
    ]
    employee_parental_leave_path_slugs = [
        "gri-social-parental_leave-401-3a-3b-3c-3d-parental_leave"
    ]
    diversity_slug = "gri-social-diversity_of_board-405-1b-number_of_employee"

    
    def get(self, request):
        try:
            start = request.query_params.get('start')
            end = request.query_params.get('end')
            self.start = datetime.fromisoformat(start) if start else None
            self.end = datetime.fromisoformat(end) if end else None
            if not start or not end:
                return Response({"error": "Both 'start' and 'end' dates are required."}, status=status.HTTP_400_BAD_REQUEST)

            org_id = request.query_params.get('organisation')
            corp_id = request.query_params.get('corporate')
            loc_id = request.query_params.get('location')
            if not org_id:
                return Response({"error": "Organisation ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            organization = Organization.objects.filter(id=org_id).first() if org_id else None
            corporate = Corporateentity.objects.filter(id=corp_id).first() if corp_id else None
            location = Location.objects.filter(id=loc_id).first() if loc_id else None

            context_filters = get_raw_response_filters(
                organisation=organization,
                corporate=corporate,
                location=location,
            )

            client_id = request.user.client.id

            date_filters = filter_by_start_end_dates(
                self.start.date() if self.start else None,
                self.end.date() if self.end else None
            )

            # New Employee Hires
            filters = Q(client_id=client_id) & Q(path__slug__in=self.new_employee_hire_path_slugs) & context_filters & date_filters
            new_hire_dps = DataPoint.objects.filter(filters)

            # Employee Turnover
            turnover_filters = Q(client_id=client_id) & Q(path__slug__in=self.employee_turnover_path_slugs) & context_filters & date_filters
            turnover_dps = DataPoint.objects.filter(turnover_filters)

            # Employee Benefits
            benefits_filters = Q(client_id=client_id) & Q(path__slug__in=self.employee_benefits_path_slugs) & context_filters & date_filters
            benefits_dps = DataPoint.objects.filter(benefits_filters)

            # Parental Leave
            parental_filters = Q(client_id=client_id) & Q(path__slug__in=self.employee_parental_leave_path_slugs) & context_filters & date_filters
            parental_leave_dps = DataPoint.objects.filter(parental_filters)

            logger.info("Filters applied. Fetching employment data.")

            return Response({
                "data": {
                    "success_true": "true",
                    "new_employee_hires": self.get_new_employee_hires(new_hire_dps),
                    "employee_turnover": self.get_employment_turnover(turnover_dps),
                    "benefits": self.get_benefits(benefits_dps),
                    "parental_leave": self.get_parental_leave(parental_leave_dps),
                    "return_to_work_rate_and_retention_rate_of_employee": self.get_return_to_work_and_retention_rate(parental_leave_dps),
                    "number_of_employee_per_employee_category": self.get_diversity_of_the_board(self.diversity_slug),
                }
            }, status=status.HTTP_200_OK)

        except ValueError as ve:
            logger.error(f"Invalid date format: {ve}")
            return Response({"error": "Invalid date format. Expected ISO format (YYYY-MM-DD)."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Unexpected error in EmploymentAnalyzeView1.")
            return Response({"error": "Something went wrong while processing your request.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def get_new_employee_hires(self, dps):
       
        result = []
        labels = ["Permanent employee", "Temporary employee", "Non guaranteed employee",
                  "Full Time employee", "Part time employee"]
        for label, slug in zip(labels, self.new_employee_hire_path_slugs):
            subset = dps.filter(path__slug=slug)
            total = subset.filter(metric_name="total").aggregate(sum=Sum("number_holder"))['sum'] or 0
            if total == 0:
                continue
            result.append({
                "type_of_employee": label,
                "percentage_of_male_employee": format_float(safe_divide_percentage(subset.filter(index=0, metric_name="total").aggregate(sum=Sum("number_holder"))['sum'] or 0, total)),
                "percentage_of_female_employee": format_float(safe_divide_percentage(subset.filter(index=1, metric_name="total").aggregate(sum=Sum("number_holder"))['sum'] or 0, total)),
                "percentage_of_non_binary_employee": format_float(safe_divide_percentage(subset.filter(index=2, metric_name="total").aggregate(sum=Sum("number_holder"))['sum'] or 0, total)),
                "yearsold30": format_float(safe_divide_percentage(subset.filter(metric_name="yearsold30").aggregate(sum=Sum("number_holder"))['sum'] or 0, total)),
                "yearsold50": format_float(safe_divide_percentage(subset.filter(metric_name="yearsold50").aggregate(sum=Sum("number_holder"))['sum'] or 0, total)),
                "yearsold30to50": format_float(safe_divide_percentage(subset.filter(metric_name="yearsold30to50").aggregate(sum=Sum("number_holder"))['sum'] or 0, total)),
                "total": float(total)
            })
        result.append({"type_of_employee": "Total", "total": sum(x['total'] for x in result)})
        return result

    def get_employment_turnover(self, dps):
        result = []
        labels = [
            "Permanent employee", 
            "Temporary employee", 
            "Non Guaranteed employee",
            "Full time employee", 
            "Part time employee"
        ]

        for label, slug in zip(labels, self.employee_turnover_path_slugs):
            subset = dps.filter(path__slug=slug)

            if not subset.exists():
                continue

            # Pre-load all subset values into a dictionary to avoid multiple DB hits
            subset_map = {(dp.index, dp.metric_name): dp.number_holder for dp in subset}

            # Calculate beginning and end employees
            beginning_total = subset.filter(metric_name="beginning").aggregate(sum=Sum("number_holder"))['sum'] or 0
            end_total = subset.filter(metric_name="end").aggregate(sum=Sum("number_holder"))['sum'] or 0

            avg_headcount = (beginning_total + end_total) / 2 if (beginning_total + end_total) > 0 else 0
            avg_headcount = math.floor(avg_headcount)
            if avg_headcount == 0:
                continue

            # Male, Female, Non-Binary left employees
            male_left_total = (
                subset_map.get((0, "yearsold30"), 0) +
                subset_map.get((0, "yearsold30to50"), 0) +
                subset_map.get((0, "yearsold50"), 0)
            )

            female_left_total = (
                subset_map.get((1, "yearsold30"), 0) +
                subset_map.get((1, "yearsold30to50"), 0) +
                subset_map.get((1, "yearsold50"), 0)
            )

            non_binary_left_total = (
                subset_map.get((2, "yearsold30"), 0) +
                subset_map.get((2, "yearsold30to50"), 0) +
                subset_map.get((2, "yearsold50"), 0)
            )

            # Age group turnover
            yearsold30 = (
                subset_map.get((0, "yearsold30"), 0) +
                subset_map.get((1, "yearsold30"), 0) +
                subset_map.get((2, "yearsold30"), 0)
            )

            yearsold30to50 = (
                subset_map.get((0, "yearsold30to50"), 0) +
                subset_map.get((1, "yearsold30to50"), 0) +
                subset_map.get((2, "yearsold30to50"), 0)
            )

            yearsold50 = (
                subset_map.get((0, "yearsold50"), 0) +
                subset_map.get((1, "yearsold50"), 0) +
                subset_map.get((2, "yearsold50"), 0)
            )

            result.append({
                "type_of_employee": label,
                "percentage_of_male_employee": format_float(safe_divide_percentage(male_left_total, avg_headcount)),
                "percentage_of_female_employee": format_float(safe_divide_percentage(female_left_total, avg_headcount)),
                "percentage_of_non_binary_employee": format_float(safe_divide_percentage(non_binary_left_total, avg_headcount)),
                "yearsold30": format_float(safe_divide_percentage(yearsold30, avg_headcount)),
                "yearsold30to50": format_float(safe_divide_percentage(yearsold30to50, avg_headcount)),
                "yearsold50": format_float(safe_divide_percentage(yearsold50, avg_headcount)),
                "total": float(avg_headcount)
            })

        result.append({
            "type_of_employee": "Total",
            "total": sum(x['total'] for x in result)
        })

        return result





    def get_benefits(self, dps):
        return {
            "benefits_full_time_employees": collect_data_by_raw_response_and_index(dps.filter(path__slug__endswith="_tab_1")),
            "benefits_part_time_employees": collect_data_by_raw_response_and_index(dps.filter(path__slug__endswith="_tab_2")),
            "benefits_temporary_employees": collect_data_by_raw_response_and_index(dps.filter(path__slug__endswith="_tab_3")),
        }

    def get_parental_leave(self, dps):
        items = collect_data_by_raw_response_and_index(dps)
        # Manual index -> label mapping
        index_to_category = {
            0: "Parental Leave Entitlement",
            1: "Taking Parental Leave",
            2: "Returning to work Post leave",
            3: "Retained 12th month after leave"
        }
        
        result = []
        for i, itm in enumerate(items):
            result.append({
                "employee_category": index_to_category.get(i, "Unknown"),
                "male": int(itm.get('male', 0)),
                "female": int(itm.get('female', 0)),
                "total": int(itm.get('male', 0)) + int(itm.get('female', 0))
            })
        return result
    
    def get_return_to_work_and_retention_rate(self, dps):
        result = []
        # collect raw response first
        items = collect_data_by_raw_response_and_index(dps)
        # Safely convert values to integers
        taking_male = int(items[1].get("male", 0))  # Index 1 is 'Taking Parental Leave'
        taking_female = int(items[1].get("female", 0))

        return_post_male = int(items[2].get("male", 0))  # Index 2 is 'Returning to work Post leave'
        return_post_female = int(items[2].get("female", 0))
        retained_male = int(items[3].get("male", 0))  # Index 3 is 'Retained 12th month after leave'
        retained_female = int(items[3].get("female", 0))
        # Return to work rate
        return_to_work = {
            "employee_category": "Return to work rate",
            "male": format_float(safe_divide_percentage(return_post_male, taking_male)),
            "female": format_float(safe_divide_percentage(return_post_female, taking_female)),
        }
        result.append(return_to_work)
        # Retention rate
        retention = {
            "employee_category": "Retention rate",
            "male": format_float(safe_divide_percentage(retained_male, return_post_male)),
            "female": format_float(safe_divide_percentage(retained_female, return_post_female)),
        }
        result.append(retention)
        return result


    def get_diversity_of_the_board(self, slug):
        dps = DataPoint.objects.filter(path__slug=slug)
        items = collect_data_by_raw_response_and_index(dps)
        return [
            {
                "Category": itm['category'],
                "percentage_of_female_with_org_governance": format_float(safe_divide_percentage(int(itm['female']), int(itm['totalGender']))),
                "percentage_of_male_with_org_governance": format_float(safe_divide_percentage(int(itm['male']), int(itm['totalGender']))),
                "percentage_of_non_binary_with_org_governance": format_float(safe_divide_percentage(int(itm['nonBinary']), int(itm['totalGender']))),
                "percentage_of_employees_within_30_age_group": format_float(safe_divide_percentage(int(itm['lessThan30']), int(itm['totalAge']))),
                "percentage_of_employees_within_30_to_50_age_group": format_float(safe_divide_percentage(int(itm['between30and50']), int(itm['totalAge']))),
                "percentage_of_employees_more_than_50_age_group": format_float(safe_divide_percentage(int(itm['moreThan50']), int(itm['totalAge']))),
                "percentage_of_employees_in_minority_group": format_float(safe_divide_percentage(int(itm['minorityGroup']), int(itm['minorityGroup']) + int(itm['vulnerableCommunities']))),
                "percentage_of_employees_in_vulnerable_communities": format_float(safe_divide_percentage(int(itm['vulnerableCommunities']), int(itm['minorityGroup']) + int(itm['vulnerableCommunities'])))
            } for itm in items
        ]