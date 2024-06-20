import os

from datetime import timedelta

from celery import Celery

app = Celery('wallet')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
