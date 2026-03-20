#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="/etc/thepeach/thepeach.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE" >&2
  exit 1
fi

set -a
. "$ENV_FILE"
set +a
export DJANGO_SETTINGS_MODULE=project.settings.prod

/home/cskang/miniconda3/envs/dj5/bin/python manage.py check
curl --silent --show-error --fail http://127.0.0.1:8001/api/v1/health/
systemctl --user status gunicorn_thepeach.service --no-pager --lines=0
sudo systemctl status nginx --no-pager --lines=0
sudo systemctl status cloudflared --no-pager --lines=0
