from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator


from users.models import Follow
from recipes.models import (
    Tag,
    Recipe,
    FavoriteRecipe,
    ShoppingList,
    Ingredient,
    RecipeIngredient,
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
        user = self.context.get("request").user
        if user:
            return Follow.objects.filter(user=user, follower=obj).exists()
        return False

    # def get_is_subscribed(self, follower):
    #     user = self.context.get("request").user
    #     if user.is_authenticated:
    #         return Follow.objects.filter(
    #             user=user, follower=follower
    #         ).exists()
    #     return False

    def validate_username(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError("Использовать имя me запрещено")
        return username

    # def to_representation(self, instance):
    #         data = super().to_representation(instance)
    #         return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = (
            "ingredient",
            "amount",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredient_data = representation.pop("ingredient")
        representation.update(ingredient_data)
        representation.move_to_end("amount")
        return representation


class RecipeGetSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipeingredient_set"
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
            "author",
            "ingredients",
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


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    current_password = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"current_password": "Введен неверный пароль"}
            )
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()

        return instance


class RecipeLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )



class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("email", "username")

    # def validate_subscription(self, value):
    #     user = self.context.get("request").user
    #     auth = self.instance
    #     if value == user:
    #         raise serializers.ValidationError(
    #             "Нельзя подписаться на самого себя"
    #         )
    def get_recipes(self, obj):
        recipes_limit = self.context["request"].GET.get("recipes_limit")
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeLightSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()