# Generated by Django 4.0.6 on 2023-12-04 09:51

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rezerwacja_nip_app', '0012_alter_niprecord_data_koncowa_alter_niprecord_nazwa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='niprecord',
            name='data_koncowa',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 2, 9, 51, 6, 430729, tzinfo=utc)),
        ),
    ]
