#!/usr/bin/env bash
set -e

echo "Running database migrations..."
for i in {1..10}; do
    if python manage.py migrate --noinput; then
        break
    fi

    if [ "$i" -eq 10 ]; then
        echo "Migrations failed after ${i} attempts. Exiting."
        exit 1
    fi

    echo "Migrations failed (attempt ${i}/10). Retrying in 5s..."
    sleep 5
done

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

echo "Starting gunicorn..."
exec gunicorn dukango.wsgi:application --bind 0.0.0.0:${PORT:-8000}
