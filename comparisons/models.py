from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Species(models.Model):
    name = models.CharField(max_length=40, unique=True)
    code = models.CharField(max_length=2, unique=True)


class SequenceSet(models.Model):
   species = models.ForeignKey(Species, models.PROTECT)
   created_by = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
   created_at = models.DateTimeField(auto_now_add=True)
   modified_at = models.DateTimeField(auto_now=True)
   sequences = models.JSONField(blank=True, default=list)
   
   class Meta:
      ordering = ['-modified_at']

   def __str__(self):
      return self.sequences


class Comparison(models.Model):

    STATUSES = [
       ('NEW', 'New'),
       ('READY', 'Ready'),
       ('RUNNING', 'Running'),
       ('SUCCESS', 'Successfully finished'),
       ('ERROR', 'Error'),
   ]

    ANALYSIS_TYPES = [
       ('cgmlst', 'cgMLST'),
       ('SNP', 'SNP'),
   ]

    class Meta:
        ordering = ['-pk']

    created_by = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sequence_set = models.ForeignKey(SequenceSet, models.PROTECT)
    data_fields = ArrayField(models.CharField(max_length=25), blank=True, null=True)   # default=get_default_data_fields
    field_data = models.JSONField(blank=True, default=dict)
    status = models.CharField(max_length=15, choices=STATUSES, default='NEW')
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    elapsed_time = models.DateTimeField(blank=True, null=True)
    error_msg = models.CharField(max_length=80, blank=True, null=True)
    folder_path = models.FilePathField(blank=True, null=True)
    newick = models.TextField(blank=True, null=True)
    analysis_type = models.CharField(max_length=6, choices=ANALYSIS_TYPES)
    analysis_subtype = models.CharField(max_length=10, blank=True, null=True)
    analysis_params = models.JSONField(blank=True, default=dict)
    microreact_project = models.CharField(max_length=20, blank=True, null=True)
