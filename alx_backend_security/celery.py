# alx_backend_security/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_security.settings")

app = Celery("alx_backend_security")

# Load settings from Django, prefixing Celery-related ones with "CELERY_"
app.config_from_object("django.conf:settings", namespace="CELERY")

# Discover tasks in all installed Django apps
app.autodiscover_tasks()


# Periodic tasks schedule
app.conf.beat_schedule = {
    "detect-suspicious-activity-hourly": {
        "task": "ip_tracking.tasks.detect_suspicious_activity",
        "schedule": crontab(minute=0, hour="*"),  # every hour, at minute 0
    },
}

# Optional: timezone for periodic tasks
app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    """
    A simple debug task to check Celery worker is running.
    Usage:
        from alx_backend_security.celery import debug_task
        debug_task.delay()
    """
    print(f"Request: {self.request!r}")
