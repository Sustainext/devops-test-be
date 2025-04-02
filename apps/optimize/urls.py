from django.urls import path, include
from rest_framework import routers
from .Views.ScenarioView import ScenarioView
from .Views.BusinessMetricView import BusinessMetricView
from .Views.FetchAllEmissionData import FetchEmissionData

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
]
