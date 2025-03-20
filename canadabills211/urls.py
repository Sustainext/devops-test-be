from django.urls import path, include
from canadabills211.views.CanadaBillS211View import IIScreenViewset, ARScreenViewset
from rest_framework import routers
from canadabills211.views.GetCanadaSection import (
    GetCanadaSection,
    CorporateListCanadaData,
)
from canadabills211.views.GenerateExcel import GenerateExcel

router = routers.DefaultRouter()
router.register(
    r"identifying-information", IIScreenViewset, basename="Identifying_Information"
)
router.register(r"annual-report", ARScreenViewset, basename="Annual_Report")
urlpatterns = [
    path("", include(router.urls)),
    path("canada_section/", GetCanadaSection.as_view(), name="canada_section"),
    path("corporate_list/", CorporateListCanadaData.as_view(), name="corporate_list"),
    path("generate_cbill_excel/", GenerateExcel.as_view(), name="generate_cbill_excel"),
]
