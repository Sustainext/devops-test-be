from analysis.utils.Social.emloyment import employment_analysis
from datametric.models import RawResponse


def create_analysis_data(raw_response: RawResponse):
    employment_analysis(raw_response=raw_response)
