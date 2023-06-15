from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Follow
from .serializers import SubscriptionSerializer

User = get_user_model()


class SubscribeViewSet(APIView):
    """APIView для кастомной модели пользователя."""

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
    """ListAPIView для подписок пользователей."""

    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(follower__user=user)
