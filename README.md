# Клуб собак

Демо на **Django** для портфолио: пользователи, карточки собак, поиск, отзывы и модерация.

Другие работы: [лендинги](https://alexandr-mailru.github.io/landings-portfolio/) · [магазин](https://github.com/Alexandr-mailru/severny-shop)

## Возможности

- Регистрация / вход / профиль с аватаром
- CRUD собак и родословных
- Поиск и сортировка, кэш (locmem или Redis)
- Отзывы + модерация, роли user / moderator / admin
- Политика конфиденциальности (ФЗ‑152), согласие при регистрации, баннер cookie

## Персональные данные и cookie

- Обязательное согласие на обработку ПДн при регистрации
- Технические cookie: `sessionid`, `csrftoken` (без аналитики/рекламы)
- Страница `/privacy/`
- Секреты только из `.env` (см. `.env_sample`)

## Стек

Python 3.12+ · Django 4.2 · SQLite (по умолчанию) · WhiteNoise · Pillow · Gunicorn  
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

## Переменные окружения

См. `.env_sample`. Для MSSQL: `USE_MSSQL=1` и `DB_*`. Для Redis: `REDIS_URL=...`.  
В проде: `DEBUG=False`, свой `SECRET_KEY`, `ALLOWED_HOSTS`, при HTTPS — `CSRF_TRUSTED_ORIGINS`.

## Структура

```
myproject/   настройки и URL
users/       аккаунты, отзывы, модерация
dogs/        собаки и родословные
templates/   базовый шаблон и политика
static/      CSS и cookie.js
```

## Лицензия

MIT
