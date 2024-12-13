from django.urls import path, include
from canadabills211.views.CanadaBillS211View import IIScreenViewset, ARScreenViewset
from rest_framework import routers

router = routers.DefaultRouter()
router.register(
    r"identifying-information", IIScreenViewset, basename="Identifying_Information"
)
router.register(r"annual-report", ARScreenViewset, basename="Annual_Report")
urlpatterns = [
    path("", include(router.urls)),
]
