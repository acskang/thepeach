import multiprocessing

bind = "127.0.0.1:8001"
backlog = 2048

workers = min(4, max(2, multiprocessing.cpu_count()))
worker_class = "gthread"
threads = 2
worker_connections = 1000
timeout = 300
graceful_timeout = 30
keepalive = 2

max_requests = 1000
max_requests_jitter = 100

accesslog = "/logs/thepeach/gunicorn_access.log"
errorlog = "/logs/thepeach/gunicorn_error.log"
loglevel = "info"

proc_name = "thepeach"
daemon = False

preload_app = False
