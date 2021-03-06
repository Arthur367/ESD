# Generated by Django 3.2.6 on 2022-07-08 14:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('license_api', '0003_alter_licensekey_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='licensekey',
            name='key',
            field=models.UUIDField(default=uuid.UUID('fed79d8e-254b-4a9f-8591-260f0869111d')),
        ),
        migrations.AlterField(
            model_name='licensekey',
            name='maxUsers',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
