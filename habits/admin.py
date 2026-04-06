from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Настройка отображения привычек в админке"""

    # Поля для списка привычек
    list_display = (
        "id",
        "action",
        "user",
        "time",
        "place",
        "is_pleasant",
        "is_public",
        "periodicity",
    )

    # Поля для фильтра
    list_filter = ("is_pleasant", "is_public", "user", "periodicity")

    # Поля для поиска
    search_fields = ("action", "place", "user__email")

    # Поля, которые можно редактировать прямо в списке
    list_editable = ("is_pleasant", "is_public")

    # Поля только для чтения
    readonly_fields = ("id",)

    # Сортировка по умолчанию
    ordering = ("-id",)

    # Разбивка на поля в форме редактирования
    fieldsets = (
        ("Основная информация", {"fields": ("user", "action", "place", "time")}),
        (
            "Характеристики",
            {"fields": ("is_pleasant", "is_public", "periodicity", "duration")},
        ),
        (
            "Связи и вознаграждение",
            {
                "fields": ("connected_habit", "reward"),
                "description": "Заполните ТОЛЬКО ОДНО из двух полей: связанная привычка или вознаграждение",
            },
        ),
    )

    # Подсказки для полей
    def get_help_text(self, field_name):
        help_texts = {
            "duration": "Время в секундах (не более 120)",
            "periodicity": "Периодичность в днях (1-7)",
            "connected_habit": "Выберите приятную привычку",
        }
        # если для поля не задана специальная подсказка
        return help_texts.get(field_name, "")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничиваем выбор связанной привычки только привычками того же пользователя"""

        if db_field.name == "connected_habit":
            # Показываем только привычки текущего пользователя
            if request.user.is_superuser:
                kwargs["queryset"] = Habit.objects.all()
            else:
                kwargs["queryset"] = Habit.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
