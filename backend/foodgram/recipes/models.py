from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth import get_user_model 
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



class Tag(models.Model):
    """Тег рецепта"""
    name = models.CharField(
        verbose_name="name tag",
        unique=True,
        max_length=200
    )
    color = models.CharField(
        verbose_name="color tag",
        unique=True,
        max_length=7,
        help_text="Введите код color в формате HEX"
    )
    slug = models.SlugField(
        verbose_name="Slug tag",
        unique=True,
        max_length=200,
        null=True,
        validators=[RegexValidator(regex="^[-a-zA-Z0-9_]+$")]
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент для рецепта"""
    name = models.CharField(
        verbose_name="name ингредиента",
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт"""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes"
    )

    name = models.CharField(verbose_name="name рецепта", max_length=200)
    image = models.ImageField(verbose_name="Картинка", upload_to="recipes/")
    text = models.TextField(verbose_name="Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="RecipeIngregient",
        related_name="recipes"
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления min",
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class RecipeIngregient(models.Model):
    """Наличие определенного ингредиента в определенном рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Нужное количество ингредиента для рецепта",
        validators=[MinValueValidator(1)]
    )

class ShoppingCart(models.Model):
    """Корзина с рецептами"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="shopping_cart"
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Peцепт для корзины",
        on_delete=models.CASCADE,
    )


class Favorite(models.Model):
    """Избранное"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт для избранного",
        on_delete=models.CASCADE,
    )
