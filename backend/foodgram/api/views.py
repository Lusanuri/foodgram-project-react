from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          SubscriptionSerializer, TagSerializer)


class SubscriptionsViewSet(viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    queryset = User.objects.all()

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = user.follower.all().values("author")
        result = User.objects.filter(id__in=subscriptions)
        page = self.paginate_queryset(result)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        if request.method == "DELETE":
            get_object_or_404(Follow, user=request.user,
                              author=author).delete()
            return Response({"detail": "Успешная отписка"},
                            status=status.HTTP_204_NO_CONTENT)
        serializer = SubscriptionSerializer(
            author, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = [IngredientFilter]
    search_fields = ["^name"]


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("color", "birth_year")
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return RecipeCreateSerializer
        print('eeee')
        return RecipeSerializer

    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        if request.method == "DELETE":
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response({"detail": "Рецепт удален из избранного"},
                            status=status.HTTP_204_NO_CONTENT)
        serializer = RecipeShortSerializer(
            recipe,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({"errors": "Рецепт уже в избранном"},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        if request.method == "DELETE":
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {"detail": "Рецепт удален из списка покупок"},
                status=status.HTTP_204_NO_CONTENT
            )
        serializer = RecipeShortSerializer(
            recipe,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({"errors": "Рецепт уже в списке покупок"},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user).values(
            "ingredient__name", "ingredient__measurement_unit").annotate(
            total_amount=Sum("amount"))
        content_list = []
        for ingredient in ingredients:
            content_list.append(
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['total_amount']}")
        content = "Ваш список покупок:\n\n" + "\n".join(content_list)
        filename = "shopping_cart.txt"
        file = HttpResponse(content, content_type="text/plain")
        file["Content-Disposition"] = "attachment; filename={0}".format(
            filename)
        return file
