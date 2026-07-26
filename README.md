# Клуб собак

Django-проект: пользователи, карточки собак, поиск/сортировка, отзывы и модерация.

## Что умеет

- Регистрация / вход / профиль
- CRUD собак и родословных
- Поиск и сортировка
- Отзывы + модерация
- Кэш (локальный или Redis)
- Роли: user / moderator / admin

## Стек

Python 3.12+ · Django 4.2 · SQLite (по умолчанию) · WhiteNoise · Pillow  
Опционально: Redis, Microsoft SQL Server

## Быстрый старт

```bash
cd dogs-club
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
copy .env_sample .env           # Windows
# cp .env_sample .env           # Linux/macOS

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте http://127.0.0.1:8000/

## Важно по безопасности

Секреты только из `.env` (см. `.env_sample`). Не коммитьте пароли почты и `SECRET_KEY`.

## Переменные окружения

См. `.env_sample`. Для MSSQL: `USE_MSSQL=1` и параметры `DB_*`. Для Redis: `REDIS_URL=...`.

## Лицензия

MIT
