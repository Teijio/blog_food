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
    list_display = ["name", "author", "pub_date"]
    list_filter = ["author", "pub_date"]
    search_fields = ["name", "author__username"]
    inlines = [RecipeIngredientInline]
    filter_horizontal = [
        "tags",
        "ingredients",
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    pass


admin.site.register(RecipeIngredient)  # Регистрируем RecipeIngredient отдельно