from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Recipe, Tag, Ingredient, ShoppingCart, Favorite
from .serializers import (
    TagSerializer, SmallRecipeSerializer,
    IngredientSerializer, RecipeSerializer,
)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author", "tags"]

    def create_relation(self, user, recipe, model, str_name):
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"errors": f"Рецепт уже в {str_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = SmallRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, user, recipe, model, str_name):
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"errors": f"Такого рецепта нет в {str_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        pass

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Exception:
            return Response(
                {"errors": ("Такого рецепта не существует. " +
                            "Проверьте, что передали правильный id.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == "POST":
            return self.create_relation(user, recipe, ShoppingCart, "корзине")
        return self.delete_relation(user, recipe, ShoppingCart, "корзине")

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated],)
    def favorite(self, request, pk=None):
        user = self.request.user
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Exception:
            return Response(
                {"errors": ("Такого рецепта не существует. " +
                            "Проверьте, что передали правильный id.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == "POST":
            return self.create_relation(user, recipe, Favorite, "избранном")
        return self.delete_relation(user, recipe, Favorite, "избранном")

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