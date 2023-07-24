from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

User = get_user_model()

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

    @action(detail=False, permission_classes=[IsAuthenticated],)
    def subscriptions(self, request):
        pass

    @action(detail=False, methods=["post", "delete"], permission_classes=[IsAuthenticated],)
    def subscribe(self, request):
        pass
