import os 
import time
from celery import Celery 
from django.conf import settings
from django.apps import apps 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.config_from_object(settings, namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

app.conf.beat_max_loop_interval = 300