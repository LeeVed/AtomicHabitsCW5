from datetime import date, time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import Habit
from .serializers import HabitSerializer
from .tasks import check_habits_for_reminders, send_telegram_message

User = get_user_model()


# Тестируем модель
class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        """Тестовый пользователь"""

        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123"
        )

    def test_create_habit(self):
        """Тест создания привычки"""

        habit = Habit.objects.create(
            user=self.user,
            place="Ванная",
            time=time(7, 0),
            action="Чистить зубы",
            periodicity=1,
            duration=120,
        )
        self.assertEqual(habit.action, "Чистить зубы")
        self.assertEqual(habit.user, self.user)
        self.assertEqual(str(habit), "Я буду Чистить зубы в 07:00:00 в Ванная")

    def test_habit_duration_validation(self):
        """Тест валидации длительности"""

        habit = Habit(
            user=self.user,
            place="Ванная",
            time=time(7, 0),
            action="Чистить зубы",
            periodicity=1,
            duration=200,  # больше 120 секунд
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_reward_and_connected_habit_mutual_exclusion(self):
        """Тест: нельзя одновременно указать reward и connected_habit"""

        pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Ванная",
            time=time(20, 0),
            action="Принять ванну",
            is_pleasant=True,
            periodicity=7,
            duration=120,
        )

        habit = Habit(
            user=self.user,
            place="Спортзал",
            time=time(18, 0),
            action="Тренировка",
            periodicity=3,
            duration=120,
            reward="Кофе",
            connected_habit=pleasant_habit,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_periodicity_range(self):
        """Тест: периодичность от 1 до 7 дней"""

        habit = Habit(
            user=self.user,
            place="Ванная",
            time=time(7, 0),
            action="Чистить зубы",
            periodicity=10,  # больше 7
            duration=120,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()


# Тестируем сериализаторы
class HabitSerializerTest(TestCase):
    """Тесты для сериализатора HabitSerializer"""

    def setUp(self):
        """Тестовый пользователь"""
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123"
        )
        # тестовая привычка
        self.habit_data = {
            "action": "Чистить зубы",
            "place": "Ванная",
            "time": "07:00:00",
            "periodicity": 1,
            "duration": 120,
        }

    def test_valid_habit_serializer(self):
        """Тест валидных данных для создания привычки"""

        serializer = HabitSerializer(data=self.habit_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_duration_serializer(self):
        """Тест невалидной длительности"""

        self.habit_data["duration"] = 200
        serializer = HabitSerializer(data=self.habit_data)
        self.assertFalse(serializer.is_valid())
        error_msg = str(serializer.errors)
        self.assertIn("200 сек", error_msg)
        self.assertIn("120 секунд", error_msg)
        self.assertIn("не должно превышать", error_msg)


# Тестируем views
class HabitAPITest(TestCase):
    """Тесты для API привычек"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            "action": "Чистить зубы",
            "place": "Дома",
            "time": "07:00:00",
            "periodicity": 1,
            "duration": 120,
        }

    def test_create_habit(self):
        """Тест создания привычки"""

        response = self.client.post("/api/habits/", self.habit_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(Habit.objects.get().action, "Чистить зубы")

    def test_list_habits(self):
        """Тест получения списка привычек"""

        Habit.objects.create(user=self.user, **self.habit_data)
        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_unauthorized_access(self):
        """Тест доступа без авторизации"""

        self.client.force_authenticate(user=None)
        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicHabitAPITest(TestCase):
    """Тесты для публичных привычек"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="user1@test.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user1)

        self.public_habit = Habit.objects.create(
            user=self.user2,
            action="Публичная привычка",
            place="Везде",
            time=time(12, 0),
            periodicity=1,
            duration=120,
            is_public=True,
        )

    def test_see_public_habits(self):
        """Тест: пользователь видит чужие публичные привычки"""

        response = self.client.get("/api/habits/public/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Публичная привычка")


# Тестируем задачи celery
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CeleryTasksTest(TestCase):
    """Тесты для Celery задач"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123", telegram_chat_id="123456789"
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place="Ванная",
            time=time(7, 0),
            action="Чистить зубы",
            periodicity=1,
            duration=120,
        )

    @patch("habits.tasks.requests.post")
    def test_send_telegram_message(self, mock_post):
        """Тест отправки сообщения в Telegram"""

        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.return_value = None

        result = send_telegram_message("123456789", "Тестовое сообщение")
        self.assertEqual(result, "Сообщение отправлено пользователю 123456789")
        mock_post.assert_called_once()

    def test_check_habits_for_reminders(self):
        """Тест проверки привычек для напоминаний"""

        result = check_habits_for_reminders()
        self.assertIn("Обработано 1 привычек", result)

        self.habit.refresh_from_db()
        self.assertEqual(self.habit.last_reminded, date.today())

        result = check_habits_for_reminders()
        self.assertIn("Обработано 0 привычек", result)
