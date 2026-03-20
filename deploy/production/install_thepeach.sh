#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="/etc/thepeach/thepeach.env"
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"

cd "$ROOT_DIR"

sudo mkdir -p /etc/thepeach /var/www/thepeach /logs/thepeach
sudo chown cskang:www-data /logs/thepeach
sudo chmod 775 /logs/thepeach

if [ ! -f "$ENV_FILE" ]; then
  secret_key=$(/home/cskang/miniconda3/envs/dj5/bin/python - <<'PY'
import secrets

print(secrets.token_urlsafe(50))
PY
)
  tmp_env="$(mktemp)"
  cat > "$tmp_env" <<EOF
DJANGO_SECRET_KEY=${secret_key}
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=thepeach.thesysm.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://thepeach.thesysm.com
DJANGO_LOG_DIR=/logs/thepeach
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_TIME_ZONE=Asia/Seoul
POSTGRES_DB=thepeach_db
POSTGRES_USER=cskang
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=5432
THEPEACH_MEDIA_MAX_UPLOAD_BYTES=5242880
EOF
  sudo install -m 640 -o root -g cskang "$tmp_env" "$ENV_FILE"
  rm -f "$tmp_env"
  echo "Created $ENV_FILE"
fi

mkdir -p "$USER_SYSTEMD_DIR"
install -m 644 deploy/production/gunicorn_thepeach.service "$USER_SYSTEMD_DIR/gunicorn_thepeach.service"
sudo install -m 644 -o root -g root deploy/production/nginx_thepeach.conf /etc/nginx/sites-available/thepeach
sudo ln -sfn /etc/nginx/sites-available/thepeach /etc/nginx/sites-enabled/thepeach

sudo ln -sfn "$ROOT_DIR/staticfiles" /var/www/thepeach/static
sudo ln -sfn "$ROOT_DIR/media_files" /var/www/thepeach/media

if ! sudo grep -q 'hostname: thepeach.thesysm.com' /etc/cloudflared/config.yml; then
  sudo cp /etc/cloudflared/config.yml "/etc/cloudflared/config.yml.bak.thepeach.$(date +%Y%m%d%H%M%S)"
  sudo python3 - <<'PY'
from pathlib import Path

path = Path("/etc/cloudflared/config.yml")
text = path.read_text()
needle = "  - service: http_status:404\n"
block = """  # ThePeach
  - hostname: thepeach.thesysm.com
    service: http://127.0.0.1:80
    originRequest:
      httpHostHeader: thepeach.thesysm.com

"""
if "hostname: thepeach.thesysm.com" not in text:
    if needle in text:
        text = text.replace(needle, block + needle)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += block
path.write_text(text)
PY
fi

set -a
. "$ENV_FILE"
set +a
export DJANGO_SETTINGS_MODULE=project.settings.prod

/home/cskang/miniconda3/envs/dj5/bin/python manage.py collectstatic --noinput
/home/cskang/miniconda3/envs/dj5/bin/python manage.py migrate --noinput
/home/cskang/miniconda3/envs/dj5/bin/python manage.py check

sudo loginctl enable-linger cskang
systemctl --user daemon-reload
systemctl --user enable --now gunicorn_thepeach.service
systemctl --user restart gunicorn_thepeach.service
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl restart cloudflared

echo "ThePeach production deployment files installed."
