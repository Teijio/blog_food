from django.contrib import admin
from django.utils.html import format_html
from django.template.loader import render_to_string

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingList,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
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
    list_display = ["name", "colored_name"]
    search_fields = ["name"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "measurement_unit"]
    list_filter = ["name"]


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    pass


admin.site.register(RecipeIngredient)  # Регистрируем RecipeIngredient отдельно
