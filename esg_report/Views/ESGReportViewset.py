from rest_framework import viewsets
from rest_framework.views import APIView
from esg_report.models import ESGReportIntroduction
from esg_report.Serializer.ESGReportIntroductionSerializer import (
    ESGReportIntroductionSerializer,
    GetESGReportIntroductionBySectionType,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ESGReportIntroductionGETAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, esg_report_id, format=None):
        section_type_serializer = GetESGReportIntroductionBySectionType(
            data=request.query_params
        )
        section_type_serializer.is_valid(raise_exception=True)
        section_type = section_type_serializer.validated_data["section_type"]
        esg_report_introduction = ESGReportIntroduction.objects.filter(
            esg_report__id=esg_report_id,
            client=self.request.user.client,
            section_type=section_type,
        )

        serializer = ESGReportIntroductionSerializer(esg_report_introduction, many=True)
        return Response(serializer.data, status=200)


class ESGReportIntroductionPOSTAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        esg_report_introduction_serializer = ESGReportIntroductionSerializer(
            data=request.data
        )
        esg_report_introduction_serializer.is_valid(raise_exception=True)
        esg_report_introduction_serializer.save(client=self.request.user.client)
        return Response(esg_report_introduction_serializer.data, status=200)


class ESGReportIntroductionPUTAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, esg_report_id, format=None):
        section_type_serializer = GetESGReportIntroductionBySectionType(
            data=request.data
        )
        section_type_serializer.is_valid(raise_exception=True)
        section_type = section_type_serializer.validated_data["section_type"]
        esg_report_introduction = ESGReportIntroduction.objects.filter(
            esg_report__id=esg_report_id,
            client=self.request.user.client,
            section_type=section_type,
        )
        esg_report_introduction_serializer = ESGReportIntroductionSerializer(
            esg_report_introduction, data=request.data
        )
        esg_report_introduction_serializer.is_valid(raise_exception=True)
        esg_report_introduction_serializer.save(client=self.request.user.client)
        return Response(esg_report_introduction_serializer.data, status=200)


class ESGReportIntroductionChoices(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        esg_report_introduction_choices = [
            i[0] for i in ESGReportIntroduction.INTRO_SECTION_CHOICES
        ]
        return Response(esg_report_introduction_choices, status=200)
