from django.urls import include, path
from rest_framework import routers
from djoser import views as djoser_views

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    SubscribeViewSet,
    SubscribeListView,
)

router_v1 = routers.DefaultRouter()
router_v1.register(r"tags", TagViewSet, basename="tags")
router_v1.register(r"ingredients", IngredientViewSet, basename="ingredients")
router_v1.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path(
        "users/subscriptions/",
        SubscribeListView.as_view(),
        name="subscriptions",
    ),
    path(
        "users/<int:pk>/subscribe/",
        SubscribeViewSet.as_view(),
        name="subscribe",
    ),
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
