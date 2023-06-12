from django.urls import include, path

urlpatterns = [
    path("", include("api.ingredients.urls")),
    path("", include("api.recipe.urls")),
    path("", include("api.tags.urls")),
    path("", include("api.users.urls")),
]
