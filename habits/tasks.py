from datetime import date

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Habit


@shared_task
def send_telegram_message(chat_id, message):
    """
    Отправка сообщения в Telegram
    """
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return f"Сообщение отправлено пользователю {chat_id}"
    except Exception as e:
        return f"Ошибка отправки: {str(e)}"


@shared_task
def check_habits_for_reminders():
    """
    Проверка привычек, которые нужно напомнить
    (запускается по расписанию)
    """
    now = timezone.now()
    current_time = now.time()

    habits = Habit.objects.filter(
        time__lte=current_time, user__telegram_chat_id__isnull=False
    ).exclude(last_reminded=date.today())

    for habit in habits:
        send_habit_reminder.delay(habit.id)
        habit.last_reminded = date.today()
        habit.save()

    return f"Обработано {habits.count()} привычек"


@shared_task
def send_habit_reminder(habit_id):
    """
    Отправка напоминания о конкретной привычке
    """
    try:
        habit = Habit.objects.get(id=habit_id)

        message = (
            f"<b>Напоминание о привычке!</b>\n\n"
            f"Что: {habit.action}\n"
            f"Где: {habit.place}\n"
            f"Когда: {habit.time.strftime('%H:%M')}\n"
        )

        if habit.reward:
            message += f"\n🎁 Награда: {habit.reward}"
        elif habit.connected_habit:
            message += f"\n✨ После этого: {habit.connected_habit.action}"

        if habit.user.telegram_chat_id:
            send_telegram_message.delay(habit.user.telegram_chat_id, message)
            return f"Напоминание отправлено для привычки {habit_id}"
        else:
            return f"У пользователя {habit.user.id} нет Telegram chat_id"

    except Habit.DoesNotExist:
        return f"Привычка {habit_id} не найдена"
