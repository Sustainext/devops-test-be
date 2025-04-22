from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework import status
from apps.optimize.models import BusinessMetric
from apps.optimize.Serializers.BusinessMetricSerializer import BusinessMetricSerializer
from django.shortcuts import get_object_or_404
from apps.optimize.models.OptimizeScenario import Scenerio


class BusinessMetricView(APIView):
    serializer_class = BusinessMetricSerializer

    def get(self, request, scenario_id):
        try:
            scenario = get_object_or_404(Scenerio, id=scenario_id)
            metric = get_object_or_404(BusinessMetric, scenario=scenario)
            serializer = self.serializer_class(metric)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(str(e))

    def patch(self, request, scenario_id):
        try:
            metric = BusinessMetric.objects.get(scenario_id=scenario_id)
        except BusinessMetric.DoesNotExist:
            raise NotFound("BusinessMetric not found with the given scenario_id")
        except Exception as e:
            raise ValidationError(str(e))

        serializer = self.serializer_class(metric, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
