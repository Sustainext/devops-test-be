import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authentication.models import CustomUser, CustomRole
from authentication.Views.GetUserRoles import GetUserRoles
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@pytest.mark.django_db
class TestGetUserRoles:
    def setup_method(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            roles="employee",
            admin=False,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("get_user_roles")
        self.custom_role = CustomRole.objects.create(name="custom_role")

    def test_get_user_roles_authenticated(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["roles"] == "employee"
        assert response.data["custom_role"] is None
        assert response.data["admin"] is False

    def test_get_user_roles_authenticated_with_custom_role(self):
        self.user.custom_role = self.custom_role
        self.user.save()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["roles"] == "employee"
        assert response.data["custom_role"] == "custom_role"
        assert response.data["admin"] is False

    def test_get_user_roles_authenticated_with_admin(self):
        self.user.admin = True
        self.user.save()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["roles"] == "employee"
        assert response.data["custom_role"] is None
        assert response.data["admin"] is True

    def test_get_user_roles_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_roles_manager(self):
        self.user.roles = "manager"
        self.user.save()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["roles"] == "manager"
        assert response.data["custom_role"] is None
        assert response.data["admin"] is False

    def test_get_user_roles_with_permissions(self):
        content_type = ContentType.objects.get_for_model(CustomUser)
        permission = Permission.objects.create(
            codename="can_access_user_roles",
            name="Can access user roles",
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["roles"] == "employee"
        assert response.data["custom_role"] is None
        assert response.data["admin"] is False
