# Generated by Django 4.1.2 on 2022-11-23 17:52

import django.contrib.postgres.fields
from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_alter_rtjob_threshold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rtjob',
            name='threshold',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=main.models.get_default_thresholds, size=None),
        ),
    ]
