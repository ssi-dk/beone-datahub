# Generated by Django 4.1.2 on 2023-05-12 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0029_rename_sequence_set_cluster_sequence_group_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cluster',
            name='sequence_group',
        ),
    ]