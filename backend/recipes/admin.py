from django.contrib import admin

from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели рецептов в admin панели."""

    list_display = ["name", "author", "get_favorite_count"]
    list_filter = ["author", "name", "tags"]
    search_fields = ["name", "author__username"]
    inlines = [RecipeIngredientInline]
    filter_horizontal = [
        "tags",
    ]

    @admin.display(description="Добавлен в избранное.")
    def get_favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение модели тагов в admin панели."""

    list_display = ["name", "colored_name"]
    search_fields = ["name"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингридиентов пользователей в admin панели."""

    list_display = ["id", "name", "measurement_unit"]
    list_filter = ["name"]


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Отображение модели избранных рецептов в admin панели."""

    pass


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Отображение модели покупок в admin панели."""

    pass


admin.site.register(RecipeIngredient)
