# Generated by Django 4.2.8 on 2024-01-04 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rezerwacja_nip_app", "0022_niprecord_nip"),
    ]

    operations = [
        migrations.AlterField(
            model_name="niprecord",
            name="nip",
            field=models.CharField(max_length=10),
        ),
    ]
