import base64

from django.core.files.base import ContentFile
from recipes.models import Recipe
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
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientSerializer(read_only=True, many=True)

    class Meta:
        model = Recipe
        fields = (
            "author", "name", "image", "text", "ingredients", "tag",
            "cooking_time", "is_favorited", "is_in_shopping_cart"
        )