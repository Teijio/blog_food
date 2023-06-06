from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters, status, viewsets, generics
from rest_framework.response import Response

# from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action, api_view, permission_classes

from recipes.models import Tag, Recipe, Ingredient, FavoriteRecipe
from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    FavoriteRecipeSerializer,
    RecipeSerializer,
)
from .filters import RecipeFilter


from users.models import Follow

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        return {"request": self.request}

    def get_permissions(self):
        if self.action == "retrieve":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        user = self.get_object()
        follower = request.user

        user_id = pk
        follower = request.user
        try:
            user = User.objects.get(id=user_id)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "POST":
            if follower == user:
                return Response(
                    {"errors": "Вы не можете подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            follow, created = Follow.objects.get_or_create(
                user=follower,
                follower=user,
            )
            if not created:
                return Response(
                    {"errors": "Вы уже подписаны на этого автора."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = SubscriptionSerializer(
                user, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "DELETE":
            try:
                follow = Follow.objects.get(user=follower, follower=user)
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Follow.DoesNotExist:
                return Response(
                    {"errors": "Вы не подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(detail=False, methods=["GET"])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(follower__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe_id = pk

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "POST":
            favorite, created = FavoriteRecipe.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                return Response(
                    {"detail": "Рецепт уже добавлен в избранное."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FavoriteRecipeSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            try:
                favorite = FavoriteRecipe.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except FavoriteRecipe.DoesNotExist:
                return Response(
                    {"detail": "Рецепт не найден в избранном."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class TagViewSet(
    generics.RetrieveAPIView, generics.ListAPIView, GenericViewSet
):
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(
    generics.RetrieveAPIView, generics.ListAPIView, GenericViewSet
):
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    serializer_class = IngredientSerializer


class SubscribeViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
