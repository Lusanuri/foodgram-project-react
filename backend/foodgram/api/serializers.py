import base64

from django.core.files.base import ContentFile
from recipes.models import Recipe, Ingredient, Tag, RecipeIngregient, ShoppingCart, Favorite
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("id", "name", "measurement_unit")

class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id", "author", "name", "image", "text", "ingredients", "tags",
            "cooking_time", "is_favorited", "is_in_shopping_cart"
        )

    def check_in_list(self, obj, model):
        request = self.context["request"]
        if not request.user.is_authenticated:
            return False
        favorite_recipe = model.objects.get(recipe=obj, user=request.user)
        if favorite_recipe:
            return True
        return False

    def get_is_favorite(self, obj):
        return self.check_in_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.check_in_list(obj, ShoppingCart)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")

class RecipePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("name", "image", "text",
                  "ingredients", "tags", "cooking_time")
        
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient)
            RecipeIngregient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient
            )
        return recipe
