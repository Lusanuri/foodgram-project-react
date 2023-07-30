from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь"""
    email = models.EmailField(
        verbose_name="Email",
        unique=True,
        max_length=254
    )
    first_name = models.CharField(
        verbose_name="Имя пользователя",
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name="Фамилия пользователя",
        max_length=150,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Подписка на автора рецептов"""
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        related_name="follower",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
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
                fields=["user", "author"],
                name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_follow",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан(а) на {self.author}"
