# Generated by Django 4.1.3 on 2022-11-27 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('united_help', '0014_eventlog_log_date_profile_organization_profile_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlog',
            name='log_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
