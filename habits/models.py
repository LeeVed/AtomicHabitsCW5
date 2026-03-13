from django.conf import settings
from django.db import models

from .validators import (
    validate_connected_habit,
    validate_duration,
    validate_habit_frequency,
    validate_pleasant_habit,
    validate_reward_and_connected_habit,
)


class Habit(models.Model):
    """Модель привычки"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="habits",
    )

    place = models.CharField(
        max_length=255,
        verbose_name="Место привычки",
        help_text="Введите место, где необходимо выполнять привычку",
    )

    time = models.TimeField(
        verbose_name="Время выполнения",
        help_text="Введите время, когда необходимо выполнять привычку",
    )

    action = models.CharField(
        max_length=250,
        verbose_name="Действие",
        help_text="Введите действие, которое представляет собой привычка",
    )

    is_pleasant = models.BooleanField(
        verbose_name="Признак приятной привычки",
        default=False,
        help_text="Отметьте, если привычка является приятной (вознаграждением)",
    )

    connected_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,  # При удалении связанной привычки ставим NULL
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой (для полезных привычек)",
        related_name="connected_to",
    )

    periodicity = models.PositiveIntegerField(
        verbose_name="Периодичность (в днях)",
        default=1,  # По умолчанию ежедневно
        help_text="Периодичность выполнения привычки в днях",
    )

    reward = models.CharField(
        max_length=500,
        verbose_name="Вознаграждение",
        blank=True,
        null=True,
        help_text="Чем вознаградить себя после выполнения",
    )

    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение (сек)",
        default=120,  # По умолчанию 2 минуты = 120 секунд
        help_text="Время на выполнение привычки",
    )

    is_public = models.BooleanField(
        verbose_name="Признак публичности",
        default=False,
        help_text="Опубликовать в общий доступ",
    )

    last_reminded = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["time"]

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.place}"

    # Унверсальная валидация
    def clean(self):
        super().clean()
        validate_reward_and_connected_habit(self)
        validate_duration(self)
        validate_connected_habit(self)
        validate_pleasant_habit(self)
        validate_habit_frequency(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
