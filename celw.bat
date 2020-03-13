@echo off
celery -A recognition worker -l DEBUG -P gevent
