from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework import filters, status, viewsets, generics
from rest_framework.response import Response

# from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action, api_view, permission_classes

from recipes.models import Tag, Recipe, Ingredient
from .serializers import (
    UserSerializer,
    SetPasswordSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    SubscriptionSerializer,
)

from users.models import Follow
from api.pagination import CustomPagination

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # pagination_class = CustomPagination

    def get_serializer_context(self):
        return {"request": self.request}

    @action(
        methods=["GET", "PATCH"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == "PATCH":
            serializer = UserSerializer(
                instance=request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        user = self.get_object()
        follower = request.user

        if request.method == "POST":
            if follower == user:
                return Response(
                    {"detail": "Вы не можете подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            follow, created = Follow.objects.get_or_create(
                user=user,
                follower=follower,
            )
            if not created:
                return Response(
                    {"detail": "Вы уже подписаны на этого автора."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "DELETE":
            try:
                follow = Follow.objects.get(user=user, follower=follower)
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Follow.DoesNotExist:
                return Response(
                    {"detail": "Вы не подписаны на этого пользователя."},
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
    serializer_class = RecipeGetSerializer


class SetPasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SetPasswordSerializer


class TagViewSet(
    generics.RetrieveAPIView, generics.ListAPIView, GenericViewSet
):
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TagSerializer


class IngredientViewSet(
    generics.RetrieveAPIView, generics.ListAPIView, GenericViewSet
):
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    serializer_class = IngredientSerializer


class SubscribeViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
