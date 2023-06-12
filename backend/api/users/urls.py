from django.urls import include, path

from .views import (
    SubscribeViewSet,
    SubscribeListView,
)

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
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
