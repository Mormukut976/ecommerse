#!/usr/bin/env bash
set -e

python manage.py migrate

python - <<'PY'
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dukango.settings')
django.setup()

from django.contrib.auth import get_user_model

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
force_reset = os.environ.get('DJANGO_SUPERUSER_FORCE_PASSWORD_RESET', '0') == '1'

if username:
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})

    changed = False
    if not user.is_active:
        user.is_active = True
        changed = True
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True

    if (created or force_reset) and password:
        user.set_password(password)
        changed = True

    if changed:
        user.save()
PY

gunicorn dukango.wsgi:application --bind 0.0.0.0:${PORT:-8000}
