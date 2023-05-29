from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )
        model = User

    def validate_username(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError("Использовать имя me запрещено")
        return username

