#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 {start|stop|restart|status|logs}" >&2
  exit 1
fi

case "$1" in
  start|stop|restart|status)
    exec systemctl --user "$1" gunicorn_thepeach.service
    ;;
  logs)
    exec journalctl --user -u gunicorn_thepeach.service -n 200 --no-pager
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs}" >&2
    exit 1
    ;;
esac
