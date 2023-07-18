# Generated by Django 4.1.9 on 2023-07-17 11:27

import bio_api.classes
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0004_rename_data_fields_comparison_tbr_data_fields_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparison',
            name='lims_data_fields',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=25), blank=True, default=bio_api.classes.LIMSMetadata.get_field_list, size=None),
        ),
        migrations.AddField(
            model_name='comparison',
            name='lims_field_data',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]