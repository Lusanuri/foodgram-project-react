from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User

        fields = (
            "email", "id", "username", "password", "first_name",
            "last_name"
        )

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomUserSerializer(CustomUserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        request_user = self.context["request"].user
        if not request_user.is_authenticated:
            return False
        if Follow.objects.filter(
            user=request_user.id, following=obj.id
        ).exists():
            return True
        return False


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count"
        )

    def get_recipes(self, obj):
        limit = self.context["request"].query_params.get("recipes_limit")
        recipe = obj.recipes.all()
        if limit:
            recipe = recipe[:int(limit)]
        serializer = SmallRecipeSerializer(recipe, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        users = User.objects.annotate(Count("recipes"))
        return users.get(id=obj.id).recipes_count


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeIngredientResponseSerializer(serializers.ModelSerializer):
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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class SmallRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = ("id", "author", "name", "image",
                  "text", "ingredients", "tags",
                  "cooking_time", "is_favorited", "is_in_shopping_cart")

    def create_ingredient_relation(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient["id"],
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

    def to_representation(self, instance):
        self.fields["tags"] = TagSerializer(many=True)
        representation = super().to_representation(instance)
        queryset = RecipeIngredient.objects.select_related(
            "ingredient"
        ).filter(recipe=instance)
        representation["ingredients"] = RecipeIngredientResponseSerializer(
            queryset, many=True
        ).data
        return representation
