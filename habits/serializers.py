from rest_framework import serializers

from .models import Habit
from .validators import (
    validate_connected_habit,
    validate_duration,
    validate_habit_frequency,
    validate_pleasant_habit,
    validate_reward_and_connected_habit,
)


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user",)

    def validate(self, attrs):
        """Валидация данных"""

        habit = Habit(**attrs)

        validate_reward_and_connected_habit(habit)
        validate_duration(habit)
        validate_connected_habit(habit)
        validate_pleasant_habit(habit)
        validate_habit_frequency(habit)

        return attrs


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только чтение)"""

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "action",
            "place",
            "time",
            "is_pleasant",
            "periodicity",
            "duration",
        ]
        read_only_fields = fields
