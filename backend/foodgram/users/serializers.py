from rest_framework import serializers

from .models import User
from api.serializers import RecipeSerializer

class UserSerializer(serializers.Serializer):
    is_subscribed = serializers.BooleanField(default=False)
    class Meta:
        model = User
        fields = ("username", "email", "id", "first_name", "last_name")

class AuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer

    class Meta:
        model = User