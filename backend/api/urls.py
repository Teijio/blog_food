from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    UserViewSet,
    SetPasswordView,
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
)

router_v1 = routers.DefaultRouter()
router_v1.register(r"users", UserViewSet, basename="users")
router_v1.register(r"tags", TagViewSet, basename="tags")
router_v1.register(r"ingredients", IngredientViewSet, basename="ingredients")
router_v1.register(r"recipes", RecipeViewSet, basename="recipes")


urlpatterns = [
    path("", include(router_v1.urls)),
    path(
        "users/set_password/",
        SetPasswordView.as_view(),
        name="set_password",
    ),
    path("auth/", include("djoser.urls.authtoken")),
    # path(
    #     "auth/token/login/",
    #     gеt_token,
    #     name="token_login",
    # ),
    # path(
    #     "auth/token/logout/",
    #     delete_token.as_view(),
    #     name="token_logout",
    # ),
]
