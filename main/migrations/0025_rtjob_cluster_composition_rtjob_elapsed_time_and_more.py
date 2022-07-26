# Generated by Django 4.0.7 on 2022-09-28 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_rename_ended_at_rtjob_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rtjob',
            name='cluster_composition',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rtjob',
            name='elapsed_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rtjob',
            name='error',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rtjob',
            name='log',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rtjob',
            name='partitions',
            field=models.TextField(blank=True, null=True),
        ),
    ]
