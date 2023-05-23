from django.conf import settings
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from rest_framework import routers

from .views import (
    Oath2LoginView,
    Oauth2RegisterView,
    Oauth2RefreshView,
    OrganizationView,
    RoleView,
    UserView,
    teams_view,
)

api_router = routers.DefaultRouter()
api_urlpatterns = [
    path("", include(api_router.urls)),
    path("oauth2/login", Oath2LoginView.as_view(), name="oauth2-login"),
    path(
        "oauth2/register", Oauth2RegisterView.as_view(), name="oauth2-register"
    ),
    path("oauth2/refresh", Oauth2RefreshView.as_view(), name="oauth2-refresh"),
    path("users/<slug:user_id>", UserView.as_view(), name="users"),
    path("organizations/", OrganizationView.as_view(), name="organizations"),
    path("roles/", RoleView.as_view(), name="roles"),
    path("teams/", teams_view, name="teams"),
]

urlpatterns = []
