from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ("ingredient", "amount")


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk",
                    "name",
                    "author",
                    )
    search_fields = ("name", "author", "author__first_name", "author__email")
    list_filter = ("tags",)
    empty_value_display = "-пусто-"
    inlines = (RecipeIngredientInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    list_editable = ("name", "slug",)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    list_editable = ("name", "measurement_unit",)
    search_fields = ("name",)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
    list_editable = ("ingredient", "amount")
    search_fields = ("ingredient",)


class FavoriteAndCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    list_editable = ("user", "recipe",)
    list_filter = ("user",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAndCartAdmin)
admin.site.register(ShoppingCart, FavoriteAndCartAdmin)
