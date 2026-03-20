#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="/etc/thepeach/thepeach.env"

cd "$ROOT_DIR"

echo "[1/4] Refreshing production env file"

secret_key=$(/home/cskang/miniconda3/envs/dj5/bin/python -c 'import secrets; print(secrets.token_urlsafe(50))')

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

if sudo test -f "$ENV_FILE"; then
  sudo cp "$ENV_FILE" "$ENV_FILE.bak.$(date +%Y%m%d%H%M%S)"
fi

sudo mkdir -p /etc/thepeach
sudo install -m 640 -o root -g cskang "$tmp_env" "$ENV_FILE"
rm -f "$tmp_env"

echo "[2/4] Installing deployment files"
bash deploy/production/install_thepeach.sh

echo "[3/4] Validating deployment"
bash deploy/production/validate_thepeach.sh

echo "[4/4] Completed"
echo "Production URL: https://thepeach.thesysm.com"
