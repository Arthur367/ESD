# Generated by Django 3.2.6 on 2022-07-08 13:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('license_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdetails',
            name='phone',
        ),
        migrations.AlterField(
            model_name='licensekey',
            name='key',
            field=models.UUIDField(default=uuid.UUID('6c5be15c-b455-41e8-b647-da7b48c163bc')),
        ),
    ]
