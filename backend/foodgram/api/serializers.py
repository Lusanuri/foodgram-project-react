import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, RecipeIngredient, Recipe, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User

        fields = (
            "email", "id", "username", "password", "first_name",
            "last_name"
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed")

    def get_is_subscribed(self, obj):
        user = get_object_or_404(
            User,
            username=self.context["request"].user
        )
        return user.follower.filter(author=obj.id).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField(source="recipes.count",
                                             read_only=True)

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count"
        )

    def get_is_subscribed(self, obj):
        user = get_object_or_404(
            User,
            username=self.context["request"].user
        )
        return user.follower.filter(author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        validators = [
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=("name", "measurement_unit")
            )
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient.id"
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipe_ingredient"
    )
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField()

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and user.favorite.filter(
            recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and user.shopping_cart.filter(
            recipe=obj.id).exists()

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "name", "text", "cooking_time", "image",
                  "is_favorited", "is_in_shopping_cart"
                )

    # def filter_favorited(self, obj):
    #     user = self.context["request"].user
    #     return user.is_authenticated and user.favorite.filter(
    #         recipe=obj.id).exists()
    #
    # def filter_shopping_cart(self, obj):
    #     user = self.context["request"].user
    #     return user.is_authenticated and user.shopping_cart.filter(
    #         recipe=obj.id).exists()


class RecipeCreateSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    def to_representation(self, instance):
        request = self.context.get("request")
        serializer = RecipeSerializer(
            instance,
            context={"request": request}
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients", "name",
                  "image", "text", "cooking_time", "is_favorited",
                  "is_in_shopping_cart")
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=("author", "name")
            )
        ]

    @staticmethod
    def save_ingredients(recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = ingredient["ingredient"]["id"]
            current_amount = ingredient["amount"]
            ingredients_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=current_amount))
        RecipeIngredient.objects.bulk_create(ingredients_list)

    def validate(self, data):
        if data["cooking_time"] <= 0:
            raise serializers.ValidationError(
                "Время приготовления не может быть менее минуты."
            )
        ingredients_list = []
        for ingredient in data["recipe_ingredient"]:
            if ingredient["amount"] <= 0:
                raise serializers.ValidationError(
                    "Количество не может быть меньше 1"
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    "Ингредиенты не должны повторяться"
                )
            ingredients_list.append(ingredient["ingredient"]["id"])
        return data

    def create(self, validated_data):
        author = self.context["request"].user
        ingredients = validated_data.pop("recipe_ingredient")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.add(*tags)
        self.save_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.image = validated_data.get("image", instance.image)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time)
        ingredients = validated_data.pop("recipe_ingredient")
        tags = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.add(*tags)
        instance.ingredients.clear()
        recipe = instance
        self.save_ingredients(recipe, ingredients)
        instance.save()
        return instance