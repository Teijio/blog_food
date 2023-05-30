from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True) 
    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password"
        )
        model = User

        extra_kwargs = {
            "username": {
                "validators": [UniqueValidator(queryset=User.objects.all())]
            },
        }

    def validate_username(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError("Использовать имя me запрещено")
        return username

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("email", "password")
        model = User
