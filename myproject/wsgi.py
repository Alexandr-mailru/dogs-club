"""WSGI for Vercel portfolio demo."""
import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
if os.environ.get("VERCEL"):
    os.environ.setdefault("SECURE_SSL_REDIRECT", "0")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

if os.environ.get("VERCEL"):
    marker = Path("/tmp/django-ready")
    if not marker.exists():
        try:
            from django.core.management import call_command

            call_command("migrate", interactive=False, verbosity=0)
            call_command("seed_demo", verbosity=0)
            marker.write_text("1", encoding="utf-8")
        except Exception as exc:
            print(f"bootstrap skipped: {exc}")
