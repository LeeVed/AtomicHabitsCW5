import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Команда, которая получает chat_id пользователей Telegram,
    чтобы отправлять сообщения конкретному пользователю.
    """

    help = "Получить Telegram chat_id от бота"

    def handle(self, *args, **options):
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getUpdates"
        response = requests.get(url)
        data = response.json()

        if data["ok"] and data["result"]:
            self.stdout.write("Найденные chat_id:")
            for update in data["result"]:
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    username = update["message"]["from"].get("username", "нет username")
                    first_name = update["message"]["from"].get("first_name", "")
                    self.stdout.write(f"- {chat_id} (@{username}) {first_name}")
        else:
            self.stdout.write("Нет сообщений. Напишите боту что-нибудь!")
