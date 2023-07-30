from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet, CustomUserViewSet)

router = DefaultRouter()

router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("recipes/<int:pk>/shopping_cart/",
         ShoppingCartViewSet.as_view({"create": "post", "destroy": "delete"})),
    path("recipes/<int:pk>/favorite/",
         FavoriteViewSet.as_view({"create": "post", "destroy": "delete"})),
    path("", include(router.urls)),
]
