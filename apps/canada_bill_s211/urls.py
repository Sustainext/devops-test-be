from django.urls import path, include

urlpatterns = [
    path("v2/",include('apps.canada_bill_s211.v2.urls'))
]
