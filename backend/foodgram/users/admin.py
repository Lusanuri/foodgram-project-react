from django.contrib import admin

from django.contrib.admin import ModelAdmin

from .models import User
from recipes.models import (
    Recipe, Tag, Ingredient, RecipeIngredient,
    ShoppingCart, Favorite
)


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "first_name",
        "last_name"
    )
    list_filter = ("email", "username")
    search_fields = ("email", "username")


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "color",
        "slug"
    )
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "measurement_unit"
    )
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "measurement_unit", "amount")

    def measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    measurement_unit.short_description = "Единица измерения"


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "count_favorites"
    )
    filter_horizontal = ("tags",)
    inlines = (IngredientInline,)
    list_display_links = ("name",)
    list_filter = ("author", "name", "tags")
    search_fields = ("name", "author__username")

    def count_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    count_favorites.short_description = "Количество добавлений в избранное"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ("id", "user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")


@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ("id", "user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
