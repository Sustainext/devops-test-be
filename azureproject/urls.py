"""azureproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from sustainapp import views, utils, signals
from django.urls import path, include
from django.conf import settings


from django.contrib.auth import views as auth_view

from django.conf.urls.static import static


from rest_framework import routers

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from sustainapp.Views.OrganisationTaskList import OrganisationTaskDashboardView
from sustainapp.Views import PreferencesView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()


router.register(r"structure", views.StructureViewset, basename="Organization")
router.register(
    r"stakeholder-group",
    views.StakeholdergroupViewset,
    basename="StakeholdergroupViewset",
)
router.register(r"stakeholder", views.StakeholderViewset, basename="stakeholder")
router.register(r"task/task", views.TaskViewSet, basename="Task")
router.register(
    r"organization_activity", views.OrganizationViewset, basename="OrganizationViewset"
)
router.register(r"corporate", views.CorporateViewset, basename="Corporate")
router.register(r"location", views.LocationViewset, basename="Location")
router.register(r"mygoal", views.MygoalViewset, basename="Mygoal")
router.register(r"mytask", views.TaskDashboardViewset, basename="TaskDashboard")
router.register(r"colour", views.ColourViewset, basename="Colour")
router.register(r"client", views.ClientViewset, basename="userclient")
# router.register(r'user_client_details', views.User_clientViewset, basename='userdetail_client')

router.register(
    r"organization_task_dashboard",
    OrganisationTaskDashboardView,
    basename="OrganisationTaskDashboard",
)

router.register(
    r"framework", PreferencesView.FrameworkReadOnlyModelViewset, basename="Framework"
)
router.register(
    r"regulation", PreferencesView.RegulationReadOnlyModelViewset, basename="Regulation"
)
router.register(
    r"target", PreferencesView.TargetReadOnlyModelViewset, basename="Target"
)
router.register(r"sdg", PreferencesView.SdgReadOnlyModelViewset, basename="Sdg")
router.register(
    r"certification",
    PreferencesView.CertificationReadOnlyModelViewset,
    basename="Certification",
)
router.register(
    r"rating", PreferencesView.RatingReadOnlyModelViewset, basename="Rating"
)


urlpatterns = [
    path("sustainapp/", include("sustainapp.urls")),
    path("api/auth/", include("authentication.urls")),
    path("admin/", admin.site.urls),
    path("organization", views.organizationonly, name="organization"),
    path(
        "corporate", views.corporateonly, name="corporateony"
    ),  # * Used for POST Call Only
    path("locationonlyview", views.locationonlyview, name="locationviewonly"),
    path("corporategetonly", views.corporategetonly, name="corporategetonly"),
    path("orggetonly", views.orggetonly, name="orggetonly"),
    path("", include(router.urls)),
    path("locationdata", views.locationview),
    # this call happens After login
    path("user_org", views.UserOrgDetails, name="UserOrgDetails"),
    path("get_org", views.get_org, name="get_org"),
    path("analyseview", views.AnalyseView, name="AnalyseView"),
    path(
        "api/trigger-signal/",
        signals.send_activation_email,
        name="send_activation_email",
    ),
    # swagger started
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # swagger ended
    path("user_profile_update/", views.UserOrgUpdateView, name="userorg_update_view"),
    path(
        "select_preference/", PreferencesView.TypeOfPreference, name="TypeOfPreference"
    ),
    path(
        "organization_preference/", PreferencesView.OrgPreference, name="OrgPreference"
    ),
    path(
        "update_organization_preference/",
        PreferencesView.UpdatePreference,
        name="UpdatePreference",
    ),
    path("datametric/", include("datametric.urls")),
    path("materiality_dashboard/", include("materiality_dashboard.urls")),
    path("refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEVELOPMENT_MODE:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
