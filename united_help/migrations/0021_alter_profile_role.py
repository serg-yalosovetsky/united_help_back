# Generated by Django 4.1.3 on 2023-01-19 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('united_help', '0020_rename_enabled_event_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.IntegerField(choices=[(0, 'Admin'), (1, 'Volunteer'), (2, 'Organizer'), (3, 'Refugee')]),
        ),
    ]