from django.urls import path, include
from rest_framework import routers
from .Views.ScenerioView import ScenerioView

router = routers.DefaultRouter()
router.register(r"scenerio", ScenerioView, basename="scenerio")

urlpatterns = [
    path("", include(router.urls)),
]
