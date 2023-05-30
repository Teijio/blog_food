from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, gеt_token

router_v1 = routers.DefaultRouter()
router_v1.register(r"users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router_v1.urls)),
    path("token/", gеt_token, name="token"),
]
