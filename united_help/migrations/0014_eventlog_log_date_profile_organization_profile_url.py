# Generated by Django 4.1.3 on 2022-11-27 22:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('united_help', '0013_remove_user_description_remove_user_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlog',
            name='log_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 28, 0, 41, 57, 303397)),
        ),
        migrations.AddField(
            model_name='profile',
            name='organization',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='url',
            field=models.TextField(blank=True, null=True),
        ),
    ]
