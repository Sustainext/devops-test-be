from django.urls import path, include
from canadabills211.views.CanadaBillS211View import IIScreenViewset
from rest_framework import routers

router = routers.DefaultRouter()
router.register(
    r"identifying-information", IIScreenViewset, basename="Identifying_Information"
)

urlpatterns = [
    path("", include(router.urls)),
]
