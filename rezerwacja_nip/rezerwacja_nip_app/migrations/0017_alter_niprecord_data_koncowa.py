# Generated by Django 4.2.8 on 2023-12-16 11:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rezerwacja_nip_app", "0016_auto_20231216_1042"),
    ]

    operations = [
        migrations.AlterField(
            model_name="niprecord",
            name="data_koncowa",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 2, 14, 11, 44, 36, 187165, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
