# Generated by Django 4.0.7 on 2022-08-23 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_dataset_description_alter_dataset_mongo_ids'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
