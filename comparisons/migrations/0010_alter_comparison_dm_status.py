# Generated by Django 4.1.9 on 2023-07-19 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0009_remove_tree_id_tree_dashboard_created_tree_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comparison',
            name='dm_status',
            field=models.CharField(choices=[('NODATA', 'No data'), ('PENDING', 'Pending'), ('VALID', 'Valid'), ('ERROR', 'Request was unsuccesful')], default='NODATA', max_length=15, verbose_name='DM status'),
        ),
    ]
