# Generated by Django 4.0.6 on 2023-10-10 16:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rezerwacja_nip_app', '0009_rename_email_klienta_niprecord_email_uzytkownika_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='niprecord',
            name='data_koncowa',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 9, 16, 11, 14, 116516, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='niprecord',
            name='status',
            field=models.CharField(choices=[('WOLNY', 'Wolny do rezerwacji'), ('ZABLOKOWANY', 'Zablokowany'), ('WYGASLO', 'Rezerwacja wygasła')], max_length=11),
        ),
    ]