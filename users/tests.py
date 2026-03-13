from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


# Тестируем модель
class CustomUserModelTest(TestCase):
    """Тесты для кастомной модели пользователя"""

    def test_create_user(self):
        """Тест создания обычного пользователя"""

        user = User.objects.create_user(
            email="test@test.com",
            password="testpass123",
            first_name="Иван",
            last_name="Петров",
        )
        self.assertEqual(user.email, "test@test.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(user.first_name, "Иван")
        self.assertFalse(user.is_staff)

    def test_create_user_without_email(self):
        """Тест: нельзя создать пользователя без email"""

        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        """Тест создания суперпользователя"""

        admin = User.objects.create_superuser(
            email="admin@test.com", password="adminpass123"
        )
        self.assertEqual(admin.email, "admin@test.com")
        self.assertTrue(admin.check_password("adminpass123"))
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str_method(self):
        """Тест строкового представления пользователя"""

        user = User.objects.create_user(email="test@test.com", password="testpass123")
        self.assertEqual(str(user), "test@test.com")

    def test_telegram_chat_id(self):
        """Тест поля telegram_chat_id"""

        user = User.objects.create_user(
            email="test@test.com", password="testpass123", telegram_chat_id="123456789"
        )
        self.assertEqual(user.telegram_chat_id, "123456789")


# Тестируем views
class UserAPITest(TestCase):
    """Тесты для API пользователей"""

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "test@test.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "Иван",
            "last_name": "Петров",
        }

    def test_register_user(self):
        """Тест регистрации пользователя"""

        response = self.client.post("/api/register/", self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@test.com")

    def test_register_with_mismatched_passwords(self):
        """Тест регистрации с несовпадающими паролями"""

        self.user_data["password2"] = "wrongpass"
        response = self.client.post("/api/register/", self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_existing_email(self):
        """Тест регистрации с уже существующим email"""

        User.objects.create_user(email="test@test.com", password="testpass123")
        response = self.client.post("/api/register/", self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """Тест авторизации пользователя"""

        User.objects.create_user(email="test@test.com", password="testpass123")

        login_data = {"email": "test@test.com", "password": "testpass123"}
        response = self.client.post("/api/login/", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
