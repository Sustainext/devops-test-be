from django.urls import path, include
from rest_framework import routers
from apps.optimize.Views.ScenarioView import ScenarioView
from apps.optimize.Views.BusinessMetricView import BusinessMetricView
from apps.optimize.Views.FetchAllEmissionData import FetchEmissionData
from apps.optimize.Views.EmissionDataExistsView import EmissionDataExistsView
from apps.optimize.Views.SelectedActivityView import SelectedActivityView
from apps.optimize.Views.CalculateClimatiqResult import CalculateClimatiqResult

router = routers.DefaultRouter()
router.register(r"scenario", ScenarioView, basename="scenario")
urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:scenario_id>/businessmetric/",
        BusinessMetricView.as_view(),
        name="business-metric-by-scenario",
    ),
    path(
        "<int:scenario_id>/emissiondata/",
        FetchEmissionData.as_view(),
        name="emission-data",
    ),
    path(
        "emissiondataexists/",
        EmissionDataExistsView.as_view(),
        name="emission-data-exists",
    ),
    path(
        "<int:scenario_id>/selectedactivity/",
        SelectedActivityView.as_view(),
        name="selected-activity",
    ),
    path(
        "<int:scenario_id>/calculateclimatiqresult/",
        CalculateClimatiqResult.as_view(),
        name="calculate-climatiq-result",
    ),
]
