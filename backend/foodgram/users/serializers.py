from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Follow

User = get_user_model()

class CustomUserCreateSerializer(serializers.ModelSerializer):
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
        from api.serializers import SmallRecipeSerializer
        limit = self.context["request"].query_params.get("recipes_limit")
        recipe = obj.recipes.all()
        if limit:
            recipe = recipe[:int(limit)]
        serializer = SmallRecipeSerializer(recipe, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        users = User.objects.annotate(Count("recipes"))
        return users.get(id=obj.id).recipes_count
