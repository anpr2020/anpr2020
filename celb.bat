@echo off
celery -A recognition beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler
