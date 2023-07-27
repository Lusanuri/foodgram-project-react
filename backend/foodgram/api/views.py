from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Recipe, Tag, Ingredient, ShoppingCart, Favorite
from .permissions import AuthorOrReadOnly
from .serializers import (
    TagSerializer, SmallRecipeSerializer,
    IngredientSerializer, RecipeSerializer,
)
from .filters import RecipeFilter

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AuthorOrReadOnly, ]
    http_method_names = ["get", "post", "patch", "delete"]
    filterset_class = RecipeFilter
    filter_backends = [DjangoFilterBackend, ]

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

    @action(detail=False,
            methods=["get"],
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        filename = "products_for_recipes.txt"
        content = "----------- Список покупок -----------\n\n"
        list_of_ingredients = {}
        cart = self.request.user.shopping_cart.select_related("recipe").all()
        recipes_in_cart = [item.recipe for item in cart]
        for recipe in recipes_in_cart:
            items = recipe.recipe_ingredient.select_related("ingredient").all()
            for item in items:
                in_list = list_of_ingredients.get(item.ingredient)
                if in_list:
                    list_of_ingredients[item.ingredient] += item.amount
                else:
                    list_of_ingredients[item.ingredient] = item.amount
        for ingredient, amount in list_of_ingredients.items():
            content += (f"* {ingredient} ({ingredient.measurement_unit})" +
                        f" — {amount}\n")
        content += "\n--------------------------------------"
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = ("attachment; " +
                                           "filename={0}".format(filename))
        return response

    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=[IsAuthenticated],)
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

    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=[IsAuthenticated],)
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