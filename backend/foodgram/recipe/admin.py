from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    fields = ('ingredient', 'amount')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'name',
                    'author',
                    )
    search_fields = ('name', 'author', 'author__first_name', 'author__email')
    list_filter = ('tags',)
    empty_value_display = '-пусто-'
    inlines = (IngredientRecipeInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_editable = ('name', 'slug',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ('name', 'measurement_unit',)
    search_fields = ('name',)


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('ingredient', 'amount')
    search_fields = ('ingredient',)


class FavoriteAndCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe',)
    list_filter = ('user',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, FavoriteAndCartAdmin)
admin.site.register(ShoppingCart, FavoriteAndCartAdmin)
