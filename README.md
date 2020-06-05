# Vehicle Monitoring and Security Systems using ANPR

Automatic Number Plate Recognition with Live Updates of process using
 - Python
 - Django
 - Tesseract OCR (Pytesseract)
 - Celery
 - Redis
 - React Frontend with Material UI
 
 
 ## Before running the project
 - Install Redis Server
     - For Ubunutu https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04
     - For windows download from https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.msi
 - Install Node modules
     - `cd frontend`
     - `npm install`
 - Install Python modules
     - `pip install -r requirements.txt`
 
 ## To run the project
 Run these in different cmd/terminal windows
 - `python manage.py runserver`
 - `celery -A recognition worker -l DEBUG -P gevent`
 - `celery -A recognition beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler`
 - `flower -A recognition -l debug --basic_auth=admin:Yashas123$ --address=127.0.0.1 --port=5555` (Optional)
 - `cd frontend && npm run start`
