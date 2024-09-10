import os

from celery import Celery
from celery.schedules import crontab

# the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_site.settings')

app = Celery('django_site')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'send_poll_results_email': {
        'task': 'polls.tasks.send_poll_results_email',
        'schedule': crontab(hour="23", minute="59"),
    },
    'send_recommended_polls_email': {
        'task': 'polls.tasks.send_recommended_polls_email',
        'schedule': crontab(day_of_week="0", hour="0", minute="0")
    }
}

# Load task modules from all registered Django app configs
app.autodiscover_tasks()
