# Generated by Django 4.1.2 on 2023-05-11 09:17

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0021_remove_comparison_data_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparison',
            name='data_fields',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=25), default=list, size=None),
            preserve_default=False,
        ),
    ]
