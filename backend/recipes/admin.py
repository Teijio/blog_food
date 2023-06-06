from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingList,
)

# @admin.register(RecipeIngredient)
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
        "ingredients",
    ]
    def get_favorite_count(self, obj):
        return obj.favorite_by.count()
    get_favorite_count.short_description = "Добавлен в избранное"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


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