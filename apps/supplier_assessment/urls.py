from django.urls import path, include
from rest_framework import routers
from apps.supplier_assessment.Views.Stakeholder import StakeholderViewSet
from apps.supplier_assessment.Views.StakeholderGroup import (
    StakeholderGroupAPI,
    StakeholderGroupEditAPI,
)
from apps.supplier_assessment.Views.ImportExportStakeholder import (
    StakeholderUploadAPIView,
    StakeholderExportAPIView,
)

router = routers.DefaultRouter()
router.register(r"stakeholder", StakeholderViewSet, basename="stakeholder")

urlpatterns = [
    path("", include(router.urls)),
    path("stakeholder-group/", StakeholderGroupAPI.as_view(), name="stakeholder-group"),
    path(
        "stakeholder-group/<int:pk>/",
        StakeholderGroupEditAPI.as_view(),
        name="stakeholder-group-edit",
    ),
    path(
        "import-stakeholder/",
        StakeholderUploadAPIView.as_view(),
        name="import-stakeholder",
    ),
    path(
        "export-stakeholder/",
        StakeholderExportAPIView.as_view(),
        name="export-stakeholder",
    ),
]
