from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited",
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )
    author = filters.NumberFilter(
        field_name="author__id",
    )

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
        conjoined=False,
    )

    class Meta:
        model = Recipe
        fields = (
            "is_favorited",
            "is_in_shopping_cart",
            "author",
            "tags",
        )

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset
