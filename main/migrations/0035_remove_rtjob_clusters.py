# Generated by Django 4.1.2 on 2022-10-26 12:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_remove_cluster_cluster_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rtjob',
            name='clusters',
        ),
    ]
