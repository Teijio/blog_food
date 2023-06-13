from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.utils.html import format_html

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов."""

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
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Цвет должен быть в формате hex-кода. Например #FFFFFF",
            )
        ],
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Слаг тэга",
    )

    @admin.display(ordering="name")
    def colored_name(self):
        return format_html(
            '<span style="color: {};">{}</span>',
            self.color,
            self.name,
        )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов."""

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
    """Модель рецептов."""

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
        through="recipeingredient",
        related_name="recipes",
        verbose_name="Ингридиенты",
    )
    cooking_time = models.PositiveSmallIntegerField(
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
    """Связующая модель между рецептами и ингридиентами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Название рецепта",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Вес/количество ингридиента",
    )

    def __str__(self):
        return f"{self.ingredient.name} ({self.recipe.name})"


class FavoriteShoppingModel(models.Model):
    """Абстрактная модель для добавления в избранное и покупки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        # null=True,
        verbose_name="Пользователь",
    )

    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class FavoriteRecipe(FavoriteShoppingModel):
    """Модель избранного."""

    class Meta(FavoriteShoppingModel.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        default_related_name = "favorites"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe",
            ),
        )


class ShoppingList(FavoriteShoppingModel):
    """Корзина покупок."""

    class Meta(FavoriteShoppingModel.Meta):
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        default_related_name = "shopping_list"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_shopping",
            )
        ]
