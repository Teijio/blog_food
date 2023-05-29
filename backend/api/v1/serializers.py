from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )
        model = User

        extra_kwargs = {
            "username": {
                "validators": [UniqueValidator(queryset=User.objects.all())]
            },
            "password": {
                "write_only": True
            }
        }
    def validate_username(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError("Использовать имя me запрещено")
        return username


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("email", "password")
        model = User
