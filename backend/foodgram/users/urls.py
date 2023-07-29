from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, login, token

router = DefaultRouter()

router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path('token/login/', login),
    path('logout/', token),
]
