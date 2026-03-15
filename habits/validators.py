from django.core.exceptions import ValidationError


def validate_reward_and_connected_habit(habit):
    """
    Проверяет, что заполнено только одно из полей:
    вознаграждение ИЛИ связанная привычка
    """
    if habit.reward and habit.connected_habit:
        raise ValidationError(
            "Нельзя заполнять одновременно и 'вознаграждение' и "
            "'связанная привычка'.Выберите что-то одно!"
        )


def validate_duration(habit):
    """
    Проверяет, что время выполнения привычки
    должно быть не больше 120 секунд
    """
    if habit.duration <= 0:
        raise ValidationError("Время выполнения должно быть положительным числом.")

    if habit.duration > 120:
        raise ValidationError(
            f"Время выполнения привычки ({habit.duration} сек) не должно "
            f"превышать 120 секунд"
        )


def validate_connected_habit(habit):
    """
    Проверяет, что в связанные привычки могут попадать
    только привычки с признаком приятной привычки.
    """
    if habit.connected_habit and not habit.connected_habit.is_pleasant:
        raise ValidationError(
            "В связанных привычках могут быть только привычки "
            "с признаком приятной привычки."
        )


def validate_pleasant_habit(habit):
    """
    Проверяет, что у приятной привычки не может быть вознаграждения
    или связанной привычки.
    """
    if habit.is_pleasant and (habit.reward or habit.connected_habit):
        raise ValidationError(
            "У приятной привычки не может быть вознаграждения "
            "или связанной привычки."
        )


def validate_habit_frequency(habit):
    """
    Проверяет, что привычка выполняется не реже,
    чем 1 раз в 7 дней (от 1 до 7 дней)
    """
    if habit.periodicity < 1 or habit.periodicity > 7:
        raise ValidationError(
            f"Периодичность выполнения должна быть от 1 до 7 дней. "
            f"Указано: {habit.periodicity} дней."
        )
