# Generated by Django 4.2.8 on 2023-12-18 19:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rezerwacja_nip_app", "0017_alter_niprecord_data_koncowa"),
    ]

    operations = [
        migrations.AlterField(
            model_name="niprecord",
            name="data_koncowa",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 2, 16, 19, 23, 13, 570188, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
