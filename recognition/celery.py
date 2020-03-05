from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recognition.settings')

APP = Celery('recognition')

APP.config_from_object('django.conf:settings', namespace='CELERY')

APP.autodiscover_tasks()

@APP.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
