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
        verbose_name="name пользователя",
        unique=True,
        max_length=150,
        validators=[RegexValidator(regex="^[\w.@+-]+\z")]
    )
    first_name = models.CharField(verbose_name="Имя", max_length=150)
    last_name = models.CharField(verbose_name="Фамилия", max_length=150)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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

    def __str__(self):
        return f"{self.user} подписан(а) на {self.following}"
