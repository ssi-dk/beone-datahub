# Generated by Django 4.0.7 on 2022-09-28 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_rtjob_pid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rtjob',
            name='status',
            field=models.CharField(choices=[('NEW', 'New'), ('READY', 'Ready'), ('RUNNING', 'Running'), ('RT_SUCCESSFUL', 'ReporTree successful'), ('ALL_DONE', 'All done'), ('OS_ERROR', 'OS error'), ('RT_ERROR', 'ReporTree error'), ('OBSOLETE', 'Obsolete')], default='NEW', max_length=15),
        ),
    ]
