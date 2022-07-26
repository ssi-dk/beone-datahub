# Generated by Django 4.1.2 on 2022-10-27 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_partition_cluster_partition'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='cluster',
            constraint=models.UniqueConstraint(fields=('partition', 'cluster_name'), name='clusters_unique_constraint'),
        ),
        migrations.AddConstraint(
            model_name='partition',
            constraint=models.UniqueConstraint(fields=('rt_job', 'name'), name='partitions_unique_constraint'),
        ),
    ]
