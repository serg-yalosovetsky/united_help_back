# Generated by Django 4.1.3 on 2023-01-31 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('united_help', '0023_event_location_display_alter_event_location_lat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='facebook_token',
            field=models.TextField(default=''),
        ),
    ]