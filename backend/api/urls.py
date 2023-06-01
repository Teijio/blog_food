from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .views import UserViewSet, SetPasswordView

router_v1 = routers.DefaultRouter()
router_v1.register(r"users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router_v1.urls)),
    path(
        "users/set_password/",
        SetPasswordView.as_view(),
        name="set_password",
    ),
    path("auth/token/login/", obtain_auth_token, name="api_token_auth"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt"))
]
