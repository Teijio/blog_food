from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db import models, transaction
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

# from drf_writable_nested import WritableNestedModelSerializer


from .utils import Base64ImageField
from users.models import Follow
from recipes.models import (
    Tag,
    Recipe,
    ShoppingList,
    Ingredient,
    RecipeIngredient,
    FavoriteRecipe,
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientForRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, follower=obj
            ).exists()
        return False

    def create(self, validated_data):
        validated_data.pop("is_subscribed", None)
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.method == "POST":
            data.pop("is_subscribed", None)
        return data


class AuthorRecipeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        return data


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                limit = int(recipes_limit)
                recipes = recipes[:limit]
            except ValueError:
                pass
        return RecipeLightSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        return data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="recipe.id")
    name = serializers.CharField(source="recipe.name")
    image = serializers.ImageField(source="recipe.image")
    cooking_time = serializers.IntegerField(source="recipe.cooking_time")

    class Meta:
        model = FavoriteRecipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = AuthorRecipeSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipeingredient_set",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        tags = self.initial_data.get("tags")
        if not tags and not ingredients:
            raise serializers.ValidationError(
                {
                    "tags": "Нужен хоть один таг для рецепта",
                    "ingredients": "Нужен хоть один ингридиент для рецепта",
                }
            )
        elif not tags:
            raise serializers.ValidationError(
                {"tags": "Нужен хоть один таг для рецепта"}
            )
        elif not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужен хоть один ингридиент для рецепта"}
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item["id"]
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    "Ингридиенты должны быть уникальными"
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item["amount"]) < 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": (
                            "Убедитесь, что значение количества "
                            "ингредиента больше 0"
                        )
                    }
                )
        data["ingredients"] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = self.initial_data.get("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get("tags")
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get("ingredients"), instance)
        instance.save()
        return instance
