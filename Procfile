web: gunicorn backend.wsgi:application -w 2 -k gevent --timeout 60 --worker-connections 100 --max-requests 1000 --max-requests-jitter 100
celery: celery -A backend.celery_app worker --loglevel=info
celery_beat: celery -A backend.celery_app beat --loglevel=info
