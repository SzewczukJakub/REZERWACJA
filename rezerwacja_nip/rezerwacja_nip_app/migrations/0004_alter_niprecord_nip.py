# Generated by Django 4.2 on 2023-09-06 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rezerwacja_nip_app', '0003_remove_niprecord_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='niprecord',
            name='nip',
            field=models.IntegerField(max_length=10, unique=True),
        ),
    ]