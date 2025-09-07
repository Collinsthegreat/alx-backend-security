web: gunicorn alx_backend_security.wsgi:application --log-file -
worker: celery -A alx_backend_security worker --loglevel=info
beat: celery -A alx_backend_security beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
