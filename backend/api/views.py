from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import action

from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    FavoriteRecipe,
    ShoppingList,
    RecipeIngredient,
)
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    FavoriteShoppingSerializer,
    RecipeSerializer,
)
from .filters import RecipeFilter, IngredientFilter
from .utils import out_list_ingredients

from users.models import Follow

User = get_user_model()


class RecipeViewSet(ModelViewSet):
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
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if request.method == "POST":
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

        if request.method == "DELETE":
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
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if request.method == "POST":
            add_to_shopping_list, created = ShoppingList.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                serializer = FavoriteShoppingSerializer(add_to_shopping_list)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"detail": "Рецепт уже добавлен в корзину."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "DELETE":
            try:
                remove_from_shopping_list = ShoppingList.objects.get(
                    user=user, recipe=recipe
                )
            except ShoppingList.DoesNotExist:
                return Response(
                    {"detail": "Рецепт не найден в корзине."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            remove_from_shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in_shop_list__user=self.request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .order_by("ingredient__name")
            .annotate(amount=Sum("amount"))
        )
        return out_list_ingredients(self, request, ingredients)


class TagViewSet(
    generics.RetrieveAPIView, generics.ListAPIView, GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = AllowAny
    pagination_class = None


class IngredientViewSet(
    generics.RetrieveAPIView, generics.ListAPIView, GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = AllowAny
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class SubscribeViewSet(APIView):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        follower = request.user

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

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
        serializer = SubscriptionSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        follower = request.user

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            follow = Follow.objects.get(user=follower, follower=user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                {"errors": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SubscribeListView(ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(follower__user=user)
