# Generated by Django 4.2.8 on 2024-01-04 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rezerwacja_nip_app", "0019_settings_alter_niprecord_data_koncowa"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="administrator",
            name="nip_limit",
        ),
    ]
