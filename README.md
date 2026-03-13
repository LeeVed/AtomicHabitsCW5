# Atomic Habits API

API-сервис для трекинга полезных привычек по книге "Атомные привычки" Джеймса Клира. 
Сервис помогает формировать полезные привычки через систему вознаграждений и Telegram-уведомлений.

##  О проекте

Проект реализует систему отслеживания привычек с валидацией по правилам "Атомных привычек":
- Полезные и приятные привычки
- Система вознаграждений и связанных привычек
- Напоминания через Telegram
- Публичные и приватные привычки

## Технологии

- **Backend**: Django 4.2, Django REST Framework
- **База данных**: PostgreSQL
- **Аутентификация**: JWT (djangorestframework-simplejwt)
- **Асинхронные задачи**: Celery, Redis
- **Документация**: drf-yasg (Swagger)
- **Тестирование**: unittest, coverage (95% покрытие)
- **Деплой**: python-dotenv, corsheaders

## Функциональность

-  Кастомная модель пользователя (регистрация по email)
-  CRUD для привычек с валидацией по правилам
-  Права доступа (владелец может всё, остальные только читать публичное)
-  Пагинация (5 привычек на странице)
-  Telegram-уведомления о привычках
-  Асинхронные задачи (Celery + Redis)
-  Полное покрытие тестами (95%)
-  Swagger-документация

## Установка и запуск

### 1. Клонирование репозитория

    git clone https://github.com/yourusername/atomic-habits.git
    cd atomic-habits

### 2. Установка зависимостей через Poetry

    poetry install
       
### 3. Настройка переменных окружения
    
    cp .env.sample .env
       
### 4. Применение миграций

    poetry run python manage.py migrate

### 5. Создание суперпользователя
       
    poetry run python manage.py createsuperuser

### 6. Запуск сервера

    poetry run python manage.py runserver

### 7. Запуск Celery (для напоминаний)

    Терминал 1: Redis
    redis-server

    Терминал 2: Celery Worker
    poetry run celery -A config worker --loglevel=info --pool=solo

    Терминал 3: Celery Beat
    poetry run celery -A config beat --loglevel=info

## API Эндпоинты

### Пользователи

    POST	/api/register/	Регистрация нового пользователя
    POST	/api/login/	Авторизация (получение JWT токенов)
    POST	/api/login/refresh/	Обновление access токена
    GET	/api/profile/	Профиль текущего пользователя
    GET	/api/users/	Список пользователей (только для админа)

### Привычки

    GET	/api/habits/	Список своих привычек (с пагинацией)	Авторизованные
    POST	/api/habits/	Создание привычки	Авторизованные
    GET	/api/habits/public/	Список публичных привычек	Авторизованные
    GET	/api/habits/{id}/	Детальная информация	Владелец или публичная
    PUT	/api/habits/{id}/	Полное обновление	Только владелец
    PATCH	/api/habits/{id}/	Частичное обновление	Только владелец
    DELETE	/api/habits/{id}/	Удаление	Только владелец

## Документация

    wagger UI: http://127.0.0.1:8000/swagger/

    ReDoc: http://127.0.0.1:8000/redoc/

## Интеграция с Telegram

### Получение chat_id пользователя

    poetry run python manage.py get_telegram_ids

## Тестирование

    poetry run python manage.py test

### Запуск с покрытием

    poetry run coverage run --source='.' manage.py test
    poetry run coverage report
    poetry run coverage html

### Текущее покрытие: 95%


##  Правила валидации привычек

    -  Время выполнения не более 120 секунд
    -  Периодичность от 1 до 7 дней
    -  Нельзя указать одновременно вознаграждение и связанную привычку
    -  Приятная привычка не может иметь вознаграждение
    -  Связанная привычка должна быть приятной


### Документация

Более подробную документацию по каждой функции можно найти в `docstrings` внутри исходного кода.

### Лицензия

Сведения о лицензии проекта (например, MIT, Apache 2.0) [укажите здесь](https://github.com).
