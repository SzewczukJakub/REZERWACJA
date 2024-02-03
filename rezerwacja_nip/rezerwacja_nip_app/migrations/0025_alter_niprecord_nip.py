# Generated by Django 4.2.8 on 2024-01-25 08:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rezerwacja_nip_app", "0024_auto_20240105_0047"),
    ]

    operations = [
        migrations.AlterField(
            model_name="niprecord",
            name="nip",
            field=models.IntegerField(
                unique=True,
                validators=[
                    django.core.validators.MinValueValidator(
                        1000000000, message="NIP must be a 10-digit number."
                    ),
                    django.core.validators.MaxValueValidator(
                        9999999999, message="NIP must be a 10-digit number."
                    ),
                ],
            ),
        ),
    ]