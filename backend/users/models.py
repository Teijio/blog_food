from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class User(AbstractUser):
    """Класс пользователей."""

    email = models.EmailField(
        max_length=254,
        unique=True,    
        verbose_name="Email",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    def clean(self):
        super().clean()
        try:
            validate_password(self.password, self)
        except ValidationError as e:
            error_messages = [error.message for error in e.error_list]
            raise ValidationError({"password": error_messages})

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=("username", "email"), name="unique_user"
            )
        ]
        ordering = ("username",)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Тот кто подписывается",
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Тот на кого подписались",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "follower"),
                name="unique_followers",
            )
        ]
