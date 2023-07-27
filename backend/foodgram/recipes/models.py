from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Тег рецепта"""
    name = models.CharField(
        verbose_name="Название тега",
        unique=True,
        max_length=200
    )
    color = models.CharField(
        verbose_name="Цвет тега",
        unique=True,
        max_length=7,
        help_text="Введите код цвета в формате HEX (например, #E26C2D)"
    )
    slug = models.SlugField(
        verbose_name="Slug тега",
        unique=True,
        max_length=200,
        validators=[RegexValidator(regex="^[-a-zA-Z0-9_]+$")],
        default=''
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент для рецепта"""
    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт"""
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes"
    )
    name = models.CharField(verbose_name="Название рецепта", max_length=200)
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="recipes/images/"
    )
    text = models.TextField(verbose_name="Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="RecipeIngredient",
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Наличие определенного ингредиента в определенном рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients"
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Нужное количество ингредиента для рецепта",
        validators=[MinValueValidator(1)],
        #default=1
    )


class ShoppingCart(models.Model):
    """Корзина с рецептами"""
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="shopping_cart_items" 
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Peцепт для корзины",
        on_delete=models.CASCADE,
    )


class Favorite(models.Model):
    """Избранное"""
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorite_recipes"
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт для избранного",
        on_delete=models.CASCADE,
    )