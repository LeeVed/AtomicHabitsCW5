import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# Настройка периодических задач (beat schedule)
app.conf.beat_schedule = {
    "check-habits-every-minute": {
        "task": "habits.tasks.check_habits_for_reminders",
        "schedule": crontab(minute="*/1"),  # Каждую минуту
    },
}
