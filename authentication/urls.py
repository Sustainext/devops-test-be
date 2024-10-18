from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
)

from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
)
from authentication.views import email_confirm_redirect, password_reset_confirm_redirect
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import path, include
from authentication.Views.CustomLoginAPI import CustomLoginView
from rest_framework import routers
from authentication.Views.UserProfile import UserProfileViewSet
from authentication.Views.ChangePassword import ChangePasswordAPIView
from authentication.Views.AzurePowerBIToken import PowerBiToken
from authentication.Views.CustomLogoutAPI import CustomLogoutView
from authentication.Views.TestigAuthentication import TestAuthentication
from authentication.Views.CustomUser import CreateCustomUserView, CheckUserExistsView, ClientUsersListView
router = routers.DefaultRouter()
router.register(r"user_profile", UserProfileViewSet, basename="UserProfile")
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
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("powerbi_token/", PowerBiToken.as_view(), name="powerbi_token"),
    path("test_authentication/", TestAuthentication.as_view(), name="test_authentication"),

    path('create-customuser/',CreateCustomUserView.as_view(), name='create-custom-user-webview'),
    path('check-user-exists/', CheckUserExistsView.as_view(),name="check-user-exists"),
    path('client-users/',ClientUsersListView.as_view(), name='client-users'),
    path("", include(router.urls)),
]
