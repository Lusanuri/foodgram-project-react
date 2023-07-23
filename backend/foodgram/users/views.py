from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(permission_classes=[IsAuthenticated],)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["post"], permission_classes=[IsAuthenticated],)
    def set_password(self, request):
        pass

    @action(permission_classes=[IsAuthenticated],)
    def subscriptions(self, request):
        pass

    @action(methods=["post", "delete"], permission_classes=[IsAuthenticated],)
    def subscribe(self, request):
        pass


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    pass


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    pass
