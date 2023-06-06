from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name="favorite_recipes__user",
        method="filter_is_favorited",
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name="shop_list__user",
        method="filter_is_in_shopping_cart",
    )
    author = filters.NumberFilter(
        field_name="author__id",
    )
    tags = filters.CharFilter(
        field_name="tags__slug",
        method="filter_tags",
    )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shop_list__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, value):
        tags = value.split(",")
        return queryset.filter(tags__slug__in=tags)

    class Meta:
        model = Recipe
        fields = [
            "is_favorited",
            "is_in_shopping_cart",
            "author",
            "tags",
        ]
