# Generated by Django 4.1.2 on 2023-05-11 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0025_potentialoutbreak_comparison'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cluster',
            name='merged_into',
        ),
    ]