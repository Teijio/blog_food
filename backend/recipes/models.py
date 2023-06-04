from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Название тэга",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Цвет тэга",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Слаг тэга",
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название ингридиента",
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to="recipe/images/",
        verbose_name="Изображение рецепта",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="recipeingredient",  # если понадобится промежуточная связь
        related_name="recipes",
        verbose_name="Ингридиенты",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления в минутах",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Название рецепта",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Вес/количество ингридиента",
    )

    def __str__(self):
        return f"{self.ingredient.name} ({self.recipe.name})"


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_by",
        verbose_name="Избранный рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite_user_recipe",
            )
        ]
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


class ShoppingList(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="shop_list",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shop_list",
        verbose_name="Рецепты в списке покупок",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_shopping",
            )
        ]
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
