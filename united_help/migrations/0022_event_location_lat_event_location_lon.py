# Generated by Django 4.1.3 on 2023-01-19 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('united_help', '0021_alter_profile_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='location_lat',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='event',
            name='location_lon',
            field=models.FloatField(default=0),
        ),
    ]
