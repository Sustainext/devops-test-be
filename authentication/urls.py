from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
)

from dj_rest_auth.views import (
    PasswordResetView,
)
from authentication.views import email_confirm_redirect, password_reset_confirm_redirect
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import UserDetailsView
from django.urls import path, include
from authentication.Views.CustomLoginAPI import CustomLoginView
from rest_framework import routers
from authentication.Views.ChangePassword import ChangePasswordAPIView
from authentication.Views.AzurePowerBIToken import PowerBiToken
from authentication.Views.CustomLogoutAPI import CustomLogoutView
from authentication.Views.TestigAuthentication import TestAuthentication
from authentication.Views.CustomUser import (
    CreateCustomUserView,
    CheckUserExistsView,
    ClientUsersListView,
)
from authentication.Views.Auth0LoginAPI import Auth0LoginView
from authentication.Views.ManageUser import ManageUserViewSet
from authentication.views import (
    get_orgs_by_client,
    get_corps_by_orgs,
    get_locs_by_corps,
)
from authentication.Views.GetUserRoles import GetUserRoles
from authentication.Views.UserProfileDetail import UserProfileDetailView
from authentication.Views.VerifyPassword import VerifyPasswordAPIView

from .Views.CustomPasswordResetViewAPI import CustomPasswordResetConfirmView
from .Views.VerifyEmail import verify_email

router = routers.DefaultRouter()
router.register(r"manage_user", ManageUserViewSet, basename="ManageUser")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="rest_register"),
    # path("login/", LoginView.as_view(), name="rest_login"),
    path("login/", CustomLoginView.as_view(), name="rest_login"),
    path("logout/", CustomLogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("register/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path(
        "register/resend-email/",
        ResendEmailVerificationView.as_view(),
        name="rest_resend_email",
    ),
    path(
        "account-confirm-email/<str:key>/",
        email_confirm_redirect,
        name="account_confirm_email",
    ),
    path(
        "account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        password_reset_confirm_redirect,
        name="password_reset_confirm",
    ),
    path(
        "password/reset/confirm/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("powerbi_token/", PowerBiToken.as_view(), name="powerbi_token"),
    path(
        "test_authentication/", TestAuthentication.as_view(), name="test_authentication"
    ),
    path(
        "create-customuser/",
        CreateCustomUserView.as_view(),
        name="create-custom-user-webview",
    ),
    path("check-user-exists/", CheckUserExistsView.as_view(), name="check-user-exists"),
    path("client-users/", ClientUsersListView.as_view(), name="client-users"),
    path("auth0-login/", Auth0LoginView.as_view(), name="auth0-login"),
    path(
        "get_orgs_by_client/<int:client_id>/",
        get_orgs_by_client,
        name="get_orgs_by_client",
    ),
    path("get_corps_by_orgs/", get_corps_by_orgs, name="get_corps_by_orgs"),
    path("get_locs_by_corps/", get_locs_by_corps, name="get_locs_by_corps"),
    path("verify_email/<str:token>/", verify_email, name="verify_email"),
    path("get_user_roles/", GetUserRoles.as_view(), name="get_user_roles"),
    path("user_profile/", UserProfileDetailView.as_view(), name="user_profile"),
    path("verify-password/", VerifyPasswordAPIView.as_view(), name="verify_password"),
    path("", include(router.urls)),
]
