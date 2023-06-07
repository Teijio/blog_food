# Generated by Django 4.2.1 on 2023-06-07 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="favoriterecipe",
            options={
                "default_related_name": "favorites",
                "verbose_name": "Избранный рецепт",
                "verbose_name_plural": "Избранные рецепты",
            },
        ),
        migrations.AlterModelOptions(
            name="shoppinglist",
            options={
                "default_related_name": "shopping_list",
                "verbose_name": "покупка",
                "verbose_name_plural": "покупки",
            },
        ),
        migrations.RemoveConstraint(
            model_name="favoriterecipe",
            name="unique_favorite_user_recipe",
        ),
        migrations.RemoveConstraint(
            model_name="shoppinglist",
            name="unique_user_recipe_shopping",
        ),
        migrations.AddConstraint(
            model_name="favoriterecipe",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_recipe"
            ),
        ),
        migrations.AddConstraint(
            model_name="shoppinglist",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping"
            ),
        ),
    ]
