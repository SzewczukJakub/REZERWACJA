# Generated by Django 4.0.6 on 2023-12-04 13:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rezerwacja_nip_app', '0013_alter_niprecord_data_koncowa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='niprecord',
            name='data_koncowa',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 2, 13, 11, 11, 702301, tzinfo=utc)),
        ),
    ]