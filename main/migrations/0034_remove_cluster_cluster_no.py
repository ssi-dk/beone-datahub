# Generated by Django 4.1.2 on 2022-10-25 13:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_remove_cluster_clusters_unique_constraint_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cluster',
            name='cluster_no',
        ),
    ]