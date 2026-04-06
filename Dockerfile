FROM python:3.13-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы зависимостей
COPY poetry.lock pyproject.toml ./

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем код проекта
COPY . .

EXPOSE 8000

# Для разработки — runserver (перезагружается при изменениях)
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]