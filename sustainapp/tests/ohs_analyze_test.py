import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authentication.models import CustomUser
from sustainapp.models import Location
from authentication.models import Client
from datametric.models import RawResponse, Path
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from collections import OrderedDict


@pytest.mark.django_db
class TestIllnessAnalyze:
    #TODO: Complete after KT of Test Cases
    def setup_method(self):
        self.client = APIClient()
        self.user_client, _ = Client.objects.get_or_create(name="TestClient")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            roles="employee",
            admin=False,
            client=self.user_client,
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse("get_illness_analysis")
        self.location = Location.objects.all().first()
        raw_response_data = (
            [
                OrderedDict(
                    [
                        ("maintypes", "Category1"),
                        ("fatalities", "1"),
                        ("recordable", "2"),
                        ("highconsequence", "3"),
                        ("employeeCategory", "4"),
                        ("numberofhoursworked", "5"),
                    ]
                ),
                OrderedDict(
                    [
                        ("maintypes", "Category2"),
                        ("fatalities", "1"),
                        ("recordable", "2"),
                        ("highconsequence", "3"),
                        ("employeeCategory", "4"),
                        ("numberofhoursworked", "5"),
                    ]
                ),
            ],
        )
        self.raw_response = {
            0: "gri-social-ohs-403-9a-number_of_injuries_emp",
            1: "gri-social-ohs-403-9b-number_of_injuries_workers",
        }
        self.number_of_injuries_employee = Path.objects.get(
            name="gri-social-ohs-403-9a-number_of_injuries_emp"
        )
        self.number_of_injuries_workers = Path.objects.get(
            name="gri-social-ohs-403-9b-number_of_injuries_workers"
        )
        self.month = 1
        self.year = 2024

        RawResponse.objects.create(
            data=raw_response_data,
            client=self.user_client,
            locale=self.location,
            year=self.year,
            path=self.number_of_injuries_employee,
            month=self.month,
        ).save()
        RawResponse.objects.create(
            data=raw_response_data,
            client=self.user_client,
            locale=self.location,
            year=self.year,
            path=self.number_of_injuries_workers,
            month=self.month,
        )

    def test_status_code_when_parameter_not_given_properly(self):
        response = self.client.get(
            self.url, filter={"start_date": "2024-01-01", "end_date": "2024-02-29"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
