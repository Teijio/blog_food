from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название тэга",
    )
    color_code = models.CharField(
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
        unique=True,
        verbose_name="Название ингридиента",
    )
    # quantity = models.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    #     verbose_name="Вес/количество ингридиента",
    # )
    # unit = models.CharField(
    #     max_length=50,
    #     verbose_name="Единица измерения",
    # )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to="recipe_images/",
        verbose_name="Изображение рецепта",
    )
    description = models.TextField(
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        on_delete=models.SET_NULL,
        through="RecipeIngredient",  # если понадобится промежуточная связь
        related_name="recipes",
        verbose_name="Ингридиенты",
    )
    preparation_time = models.IntegerField(
        verbose_name="Время приготовления в минутах"
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
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Название рецепта",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Вес/количество ингридиента",
    )
    unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения",
    )

    def __str__(self):
        return f"{self.ingredient.name} ({self.recipe.title})"


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
        unique_together = ("user", "recipe")
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
