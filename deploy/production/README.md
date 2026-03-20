## ThePeach Production Deployment Assets

These files are the source-controlled deployment assets for ThePeach.

Target topology:

- Cloudflare Tunnel
- Nginx
- Gunicorn
- Django (`project.settings.prod`)

Installed targets:

- user systemd service: `~/.config/systemd/user/gunicorn_thepeach.service`
- environment file: `/etc/thepeach/thepeach.env`
- nginx site: `/etc/nginx/sites-available/thepeach`
- nginx symlink: `/etc/nginx/sites-enabled/thepeach`
- cloudflared ingress fragment: merge into `/etc/cloudflared/config.yml`
- public nginx template: `deploy/production/nginx_thepeach_public.conf`
- internal nginx template: `deploy/production/nginx_thepeach_internal.conf`

Runtime paths:

- gunicorn bind: `127.0.0.1:8001`
- static alias root: `/var/www/thepeach/static`
- media alias root: `/var/www/thepeach/media`
- application logs: `/logs/thepeach`

Notes:

- `manage.py` remains local-development only.
- Gunicorn must set `DJANGO_SETTINGS_MODULE=project.settings.prod`.
- Secrets must live only in `/etc/thepeach/thepeach.env`.
- Gunicorn lifecycle control is user-scoped: `systemctl --user start|restart|stop gunicorn_thepeach.service`
- One-time boot persistence requires `sudo loginctl enable-linger cskang`.
- Public traffic belongs on `thepeach.thesysm.com`.
- Admin and internal auth/gateway traffic belongs on `ops.thesysm.com` or `auth-internal.thesysm.com`.
- Configure `THEPEACH_INTERNAL_REQUIRED_HEADERS` to match the Cloudflare Access headers you want Django to enforce.
- For an interactive manual deployment run, use `deploy/production/run_thepeach_deploy.sh`.
