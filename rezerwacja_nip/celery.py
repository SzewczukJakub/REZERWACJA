# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from rezerwacja_nip_app.models import NIPRecord

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rezerwacja_nip.settings')

app = Celery('rezerwacja_nip')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def update_status(self):
    # Import the necessary models and update the status here
    from rezerwacja_nip_app.models import NIPRecord
    from django.utils import timezone
    
    now = timezone.now()
    records_to_update = NIPRecord.objects.filter(data_poczatkowa__lte=now, data_koncowa__gte=now)
    
    for record in records_to_update:
        if now < record.data_poczatkowa:
            record.status = 'WOLNY'
        elif record.data_poczatkowa <= now <= record.data_koncowa:
            record.status = 'ZABLOKOWANY'
        else:
            record.status = 'WYGASLO'
        
        record.save()