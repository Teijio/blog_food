from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from recipes.models import (
    FavoriteRecipe,
    Recipe,
    RecipeIngredient,
    ShoppingList,
)
from api.permissions import IsOwnerOrReadOnly
from .filters import RecipeFilter
from .serializers import FavoriteShoppingSerializer, RecipeSerializer
from .utils import out_list_ingredients

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=(IsAuthenticated,),
        name="Add recipe to favorites",
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        favorite, created = FavoriteRecipe.objects.get_or_create(
            user=user, recipe=recipe
        )
        if not created:
            return Response(
                {"detail": "Рецепт уже добавлен в избранное."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteShoppingSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        try:
            favorite = FavoriteRecipe.objects.get(user=user, recipe=recipe)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {"detail": "Рецепт не найден в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        add_to_shopping_list, created = ShoppingList.objects.get_or_create(
            user=user, recipe=recipe
        )
        if created:
            serializer = FavoriteShoppingSerializer(add_to_shopping_list)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"detail": "Рецепт уже добавлен в корзину."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        try:
            shopping_list = ShoppingList.objects.get(user=user, recipe=recipe)
        except ShoppingList.DoesNotExist:
            return Response(
                {"detail": "Рецепт не найден в корзине."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_list__user=self.request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .order_by("ingredient__name")
            .annotate(amount=Sum("amount"))
        )
        return out_list_ingredients(self, request, ingredients)
