from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Пользователь"""
    email = models.EmailField(
        verbose_name="Email",
        unique=True,
        max_length=254
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        unique=True,
        max_length=150,
        validators=[RegexValidator(regex=r"^[\w.@+-]+$")]
    )

    class Meta:
        ordering = ["email"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Follow(models.Model):
    """Подписка на автора рецептов"""
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        related_name="follower",
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        verbose_name="Автор рецептов для подписки",
        related_name="following",
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"],
                name="unique_subscription"
            )
        ]

    def __str__(self):
        return f"{self.user} подписан(а) на {self.following}"
