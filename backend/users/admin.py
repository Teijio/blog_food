from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import Follow
from .forms import FollowForm

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Отображение модели пользователей в admin панели."""

    add_form = UserCreationForm
    model = User
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
    list_display = ("user", "follower")
    form = FollowForm
