# Generated by Django 4.1.2 on 2023-05-11 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0016_comparison_base_tool_comparison_error_msg_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparison',
            name='folder_path',
            field=models.FilePathField(allow_files=False, allow_folders=True, blank=True, null=True),
        ),
    ]