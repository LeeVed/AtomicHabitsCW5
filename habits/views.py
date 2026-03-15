from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение: владелец может редактировать, остальные только читать (для публичных)
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user

        return obj.user == request.user


class HabitPagination(PageNumberPagination):
    """Пагинация для списка привычек"""

    # по 5 привычек на страницу
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50


class HabitListCreateView(generics.ListCreateAPIView):
    """Список привычек текущего пользователя и создание новых"""

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение списка привычек текущего пользователя",
        responses={200: HabitSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создание новой привычки",
        request_body=HabitSerializer,
        responses={201: HabitSerializer()},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя"""

        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """При создании автоматически устанавливаем пользователя"""

        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование и удаление конкретной привычки"""

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_description="Получение детальной информации о привычке",
        responses={200: HabitSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Полное обновление привычки",
        request_body=HabitSerializer,
        responses={200: HabitSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление привычки",
        request_body=HabitSerializer,
        responses={200: HabitSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удаление привычки", responses={204: "No content"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        """Базовый queryset для поиска привычки"""

        return Habit.objects.all()


class PublicHabitListView(generics.ListAPIView):
    """Список публичных привычек (все пользователи)"""

    serializer_class = PublicHabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.filter(is_public=True)
