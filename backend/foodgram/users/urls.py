from django.urls import path

from .views import login, token

urlpatterns = [
    path('token/login/', login),
    path('logout/', token),
]
