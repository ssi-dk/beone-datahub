# Generated by Django 4.1.2 on 2023-06-15 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0038_rename_sequencegroup_sequenceset'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comparison',
            old_name='sequence_group',
            new_name='sequence_set',
        ),
    ]
