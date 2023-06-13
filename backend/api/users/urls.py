from django.urls import include, path

from .views import SubscribeListView, SubscribeViewSet

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
