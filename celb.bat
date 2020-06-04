@echo off
del /f celerybeat.pid
celery -A recognition beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler
