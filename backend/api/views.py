from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework import filters, status, viewsets, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action, api_view, permission_classes

from .serializers import UserSerializer, TokenSerializer, SetPasswordSerializer

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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


class SetPasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SetPasswordSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def gеt_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get("email")
    password = serializer.validated_data.get("password")
    user = get_object_or_404(User, email=email)

    if not user.check_password(password):
        return Response("Неверный пароль", status=status.HTTP_400_BAD_REQUEST)

    message = {"token": AccessToken.for_user(user)}
    return Response(message, status=status.HTTP_200_OK)
