# Generated by Django 4.1.2 on 2023-06-15 08:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comparisons', '0037_cluster_species'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SequenceGroup',
            new_name='SequenceSet',
        ),
    ]