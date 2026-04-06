from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny

from .serializers import UserRegistrationSerializer, UserSerializer

# всегда вернёт правильную модель
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveAPIView):
    """Просмотр профиля пользователя"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """Список пользователей только для админа"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
