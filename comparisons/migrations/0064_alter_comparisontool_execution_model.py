# Generated by Django 4.1.2 on 2023-07-10 12:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0063_alter_comparisontool_execution_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comparisontool',
            name='execution_model',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('direct', 'Direct'), ('mongodb_queue', 'MongoDB Queue')], max_length=13), default=list, size=None),
        ),
    ]
