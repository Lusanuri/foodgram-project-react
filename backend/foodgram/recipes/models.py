from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тега",
        max_length=200,
    )
    color = models.CharField(
        verbose_name="Цвет тега",
        max_length=7,
    )
    slug = models.SlugField(
        verbose_name="Slug тега",
        unique=True,
        max_length=200,
        null=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit"
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=200,
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="upload/",
    )
    text = models.TextField(
        verbose_name="Описание рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="RecipeIngredient",
        related_name="recipes",
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления в минутах",
        validators=[
            MinValueValidator(
                1,
                'Время приготовления не может быть менее минуты'
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "name"],
                name="unique_author_name")
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_ingredient"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
        related_name="recipe_ingredient"
    )
    amount = models.IntegerField(
        verbose_name="Нужное количество ингредиента для рецепта",
        validators=[
            MinValueValidator(1, "Количество не может быть меньше 1."),
        ],
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.ingredient}: {self.amount}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Peцепт",
        on_delete=models.CASCADE,
        related_name="cart",
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_recipe_in_cart")
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorite"
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт для избранного",
        related_name="favorite",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_recipe_in_favorited")
        ]
