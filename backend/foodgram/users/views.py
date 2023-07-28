from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow
from .serializers import SubscriptionSerializer

User = get_user_model()

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

    @action(detail=False, permission_classes=[IsAuthenticated], )
    def subscriptions(self, request):
        user = self.request.user
        queryset = user.follower.select_related("following").all()
        pages = self.paginate_queryset(queryset)
        subscriptions = [item.following for item in pages]
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
            context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


    @action(detail=True,
            methods=["post", "delete"],
            permission_classes=[IsAuthenticated],)
    def subscribe(self, request, id=None):
        user = self.request.user
        try:
            author = get_object_or_404(User, id=id)
        except Exception:
            return Response(
                {"errors": ("Такого пользователя не существует. " +
                            "Проверьте, что передали правильный id.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.id == author.id:
            return Response(
                    {"errors": ("Нельзя подписаться/отписаться. Проверьте, " +
                                "что передали id, отличный от собственного.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
        is_subscribed = Follow.objects.filter(
            user=user, following=author
        ).exists()
        if request.method == "POST":
            if is_subscribed:
                return Response(
                    {"errors": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, following=author)
            serializer = SubscriptionSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not is_subscribed:
            return Response(
                {"errors": "Вы не были подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(user=user, following=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)