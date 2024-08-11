from analysis.utils.employment_hire import (
    employment_hire_analysis,
)
from analysis.utils.employment_turnover import employment_turnover_analysis
from datametric.models import RawResponse


def create_analysis_data(raw_response: RawResponse):
    employment_hire_analysis(raw_response)
    employment_turnover_analysis(raw_response)
