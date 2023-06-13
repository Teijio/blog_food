from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class RecipeLightSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для рецептов при отписке/подписке."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для всех пользователей."""

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

    def validate_password(self, value):
        validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.method == "POST":
            data.pop("is_subscribed", None)
        return data


class AuthorRecipeSerializer(UserSerializer):
    """Сериализатор только для автора с дефолтным to_representation."""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        return data


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для подписки/отписки пользователей."""

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
            limit = int(recipes_limit)
            recipes = recipes[:limit]
        return RecipeLightSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        return data
