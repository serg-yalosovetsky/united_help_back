# Generated by Django 4.1.3 on 2022-11-07 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('united_help', '0006_remove_skill_parent_skill_parents_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='parents',
            field=models.ManyToManyField(blank=True, to='united_help.skill'),
        ),
    ]