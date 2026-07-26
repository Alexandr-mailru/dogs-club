# Клуб собак (Module 16)

Django-проект: пользователи, карточки собак, поиск/сортировка, отзывы и модерация.

Исходник: [Alexmailru195/Module16](https://github.com/Alexmailru195/Module16) — обновлённая версия для портфолио.

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
cd Module16
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

В старом репозитории в `settings.py` был **пароль почты в открытом виде**.  
В этой версии секреты только из `.env`. Если пароль приложения Яндекс когда-либо светился в GitHub — **смените его** в настройках Яндекса.

## Переменные окружения

См. `.env_sample`. Для MSSQL: `USE_MSSQL=1` и параметры `DB_*`. Для Redis: `REDIS_URL=...`.

## Лицензия

MIT
