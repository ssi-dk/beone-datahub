# Generated by Django 4.0.7 on 2022-08-15 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_rename_sample_mongo_ids_dataset_mongo_ids'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='dataset',
            name='DataSet owner and name unique together',
        ),
        migrations.AlterField(
            model_name='dataset',
            name='name',
            field=models.CharField(max_length=40, unique=True),
        ),
    ]
