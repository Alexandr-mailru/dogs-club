"""Vercel serverless entry for Django (WSGI)."""
import os

os.environ.setdefault("VERCEL", "1")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
os.environ.setdefault("SECURE_SSL_REDIRECT", "0")

from pathlib import Path

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()

_marker = Path("/tmp/django-ready")
if not _marker.exists():
    try:
        call_command("collectstatic", interactive=False, verbosity=0)
        call_command("migrate", interactive=False, verbosity=0)
        call_command("seed_demo", verbosity=0)
        _marker.write_text("1", encoding="utf-8")
    except Exception as exc:
        print(f"bootstrap skipped: {exc}")
