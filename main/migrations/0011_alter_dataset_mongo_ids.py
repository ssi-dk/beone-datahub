# Generated by Django 4.0.7 on 2022-08-23 12:10

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_dataset_mongo_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='mongo_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=24), default=list, size=None),
        ),
    ]
