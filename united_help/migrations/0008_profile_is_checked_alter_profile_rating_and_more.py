# Generated by Django 4.1.3 on 2022-11-08 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('united_help', '0007_alter_skill_parents'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='rating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='scores',
            field=models.IntegerField(default=0),
        ),
    ]
