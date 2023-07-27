from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import (
    Recipe, Ingredient, Tag, RecipeIngredient, Favorite, ShoppingCart
)


from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("id", "name", "measurement_unit")

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientInRecipeResponseSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient",
        queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source="ingredient.name")
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "author", "name", "image",
                  "text", "ingredients", "tags",
                  "cooking_time", "is_favorited", "is_in_shopping_cart")

    def create_ingredient_relation(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient["id"]),
                amount=ingredient["amount"]
            ) for ingredient in ingredients])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context["request"].user
        )
        self.create_ingredient_relation(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.image = validated_data.get("image", instance.image)
        instance.cooking_time = validated_data.get(
            "cooking_time",
            instance.cooking_time
        )
        instance.save()
        instance.tags.clear()
        instance.tags.set(validated_data["tags"])
        instance.ingredients.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.get("ingredients", instance.ingredients)
        self.create_ingredient_relation(ingredients, instance)
        instance.save()
        return instance

    def check_in_list(self, obj, model):
        request_user = self.context["request"].user
        if not request_user.is_authenticated:
            return False
        if model.objects.filter(
            user=request_user.id, recipe=obj
        ).exists():
            return True
        return False

    def get_is_favorited(self, obj):
        return self.check_in_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.check_in_list(obj, ShoppingCart)

    def to_representation(self, instance):
        self.fields["tags"] = TagSerializer(many=True)
        representation = super().to_representation(instance)
        representation["ingredients"] = IngredientInRecipeResponseSerializer(
            RecipeIngredient.objects.prefetch_related("ingredient").filter(
                recipe=instance), many=True
            ).data
        return representation
