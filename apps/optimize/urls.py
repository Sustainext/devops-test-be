from django.urls import path, include
from rest_framework import routers
from .Views.ScenarioView import ScenarioView
from .Views.BusinessMetricView import BusinessMetricView
from .Views.FetchAllEmissionData import FetchEmissionData
from .Views.EmissionDataExistsView import EmissionDataExistsView
from .Views.SelectedActivityView import SelectedActivityView

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
]
