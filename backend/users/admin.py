from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import Follow

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка для пользователей."""

    list_display = (
        "pk",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_filter = ("email", "username")
    list_per_page = settings.LIST_PER_PAGE
    search_fields = ("email", "username")
    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "follower"
    )