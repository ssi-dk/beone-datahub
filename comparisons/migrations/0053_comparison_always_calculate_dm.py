# Generated by Django 4.1.2 on 2023-06-27 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0052_remove_comparison_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparison',
            name='always_calculate_dm',
            field=models.BooleanField(default=False),
        ),
    ]