import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intra_nom035.settings.development')

app = Celery('intra_nom035')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
