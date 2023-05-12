# Generated by Django 4.2.1 on 2023-05-10 08:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comparisons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('st', models.PositiveIntegerField()),
                ('cluster_number', models.PositiveIntegerField()),
                ('subcluster', models.IntegerField(default=0)),
                ('merged_into', models.IntegerField(default=0)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('sequence_set', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='comparisons.sequenceset')),
            ],
        ),
        migrations.CreateModel(
            name='PotentialOutbreak',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('suspected_source', models.CharField(max_length=30)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='comparisons.cluster')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]