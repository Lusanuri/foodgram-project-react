from rest_framework import viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Recipe, Ingredient, Tag
from .serializers import (
    TagSerializer, RecipeCreateSerializer,
    IngredientSerializer, 
)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_favorited", "author", "is_in_shopping_cart", "tags"]

    @action(detail=False, permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        pass

    @action(detail=False, methods=["post", "delete"], permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request):
        pass

    @action(detail=False, methods=["post", "delete"], permission_classes=[IsAuthenticated],)
    def favourite(self, request):
        pass

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ["^name"]