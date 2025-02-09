from django.urls import path, include
from rest_framework import routers
from apps.supplier_assessment.Views.Stakeholder import StakeholderViewSet
from apps.supplier_assessment.Views.StakeholderGroup import StakeholderGroupAPI

router = routers.DefaultRouter()
router.register(r"stakeholder", StakeholderViewSet, basename="stakeholder")

urlpatterns = [
    path("", include(router.urls)),
    path("stakeholder-group/", StakeholderGroupAPI.as_view(), name="stakeholder-group"),
]
