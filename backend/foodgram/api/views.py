from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.shopping_list import get_shopping_list

from .filters import RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeSerializer,
    SmallRecipeSerializer, TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [AuthorOrReadOnly, ]
    filterset_class = RecipeFilter
    filter_backends = [DjangoFilterBackend, ]

    def get_queryset(self):
        queryset = Recipe.objects.select_related("author").prefetch_related(
            "ingredients"
        )
        user = self.request.user
        if user.is_authenticated:
            favorite_recipe = Favorite.objects.filter(
                user=user, recipe__pk=OuterRef("pk")
            )
            recipe_in_cart = ShoppingCart.objects.filter(
                user=user, recipe__pk=OuterRef("pk")
            )
            return queryset.annotate(
                is_favorited=Exists(favorite_recipe),
                is_in_shopping_cart=Exists(recipe_in_cart)
            )
        return queryset

    @action(detail=False,
            methods=["get"],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        cart = request.user.shopping_cart.select_related("recipe")
        shopping_cart = [item.recipe for item in cart]
        content = get_shopping_list(shopping_cart)
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment; filename={0}".format("products_for_recipes.txt")
        )
        return response


class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create_relation(self, user, recipe, model, str_name):
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response(
                {"errors": f"Рецепт уже в {str_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SmallRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, user, recipe, model, str_name):
        row_cnt, _ = model.objects.filter(user=user, recipe=recipe).delete()
        if not row_cnt:
            return Response(
                {"errors": f"Такого рецепта нет в {str_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def check_object(self, pk):
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(
                {"errors": ("Такого рецепта не существует. "
                            + "Проверьте, что передали правильный id.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return recipe

    def post(self, request, pk=None):
        user = request.user
        recipe = self.check_object(pk)
        if isinstance(recipe, Response):
            return recipe
        return self.create_relation(user, recipe, ShoppingCart, "корзине")

    def delete(self, request, pk=None):
        user = request.user
        recipe = self.check_object(pk)
        if isinstance(recipe, Response):
            return recipe
        return self.delete_relation(user, recipe, ShoppingCart, "корзине")


class FavoriteViewSet(ShoppingCartViewSet):
    def post(self, request, pk=None):
        user = request.user
        recipe = self.check_object(pk)
        if isinstance(recipe, Response):
            return recipe
        return self.create_relation(user, recipe, Favorite, "избранном")

    def delete(self, request, pk=None):
        user = request.user
        recipe = self.check_object(pk)
        if isinstance(recipe, Response):
            return recipe
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
