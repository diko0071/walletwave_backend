import os
import requests
from celery import shared_task

@shared_task()
def debug_task():
    print("Debug task")