import os


def post_fork(server, worker):
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()


def post_worker_init(worker) -> None:
    import backend.urls  # noqa


timeout = 60
workers = 4
worker_class = 'gevent'
worker_connections = 100
graceful_timeout = 600
forwarded_allow_ips = '*'
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
name = "finance-app"
bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)s "%(f)s" "%(a)s"'
max_requests = 100
max_requests_jitter = 30
limit_request_line = 8190
