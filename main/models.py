from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class DataSet(models.Model):
   species = models.CharField(max_length=20, choices=settings.ALL_SPECIES)
   owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
   name = models.CharField(max_length=40, unique=True)
   created_at = models.DateTimeField(auto_now_add=True)
   modified_at = models.DateTimeField(auto_now=True)
   description = models.CharField(max_length=200, blank=True)
   mongo_keys = models.JSONField(blank=True, default=list)

   def __str__(self):
      return self.name

def get_default_metadata_fields():
   return [
      'Outbreak_related',
      'Date_Sampling',
      'Serotype',
      'Latitude',
      'Longitude',
   ]

class RTJob(models.Model):
   STATUSES = [
        ('NEW', 'New'),
        ('READY', 'Ready'),
        ('RUNNING', 'Running'),
        ('SUCCEEDED', 'Succeeded'),
        ('FAILED', 'Failed'),
        ('INVALID', 'Invalid')
   ]
   owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
   dataset = models.ForeignKey(DataSet, models.PROTECT)
   metadata_fields = ArrayField(models.CharField(max_length=25), default=get_default_metadata_fields)
   status = models.CharField(max_length=12, choices=STATUSES, default='NEW')
   started_at = models.DateTimeField(blank=True, null=True)
   ended_at = models.DateTimeField(blank=True, null=True)
   path = models.CharField(max_length=100, blank=True, null=True)
   newick = models.TextField(blank=True, null=True)

   def initialize(self):
      self.status = 'READY'
      self.save()
      return self.status
