import pathlib

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

   def set_status(self, new_status:str):
      if new_status not in [status[0] for status in self.STATUSES]:
         raise ValueError(f"Illegal job status: {new_status}")
      self.status = new_status
      self.save()
   
   def add_sample_data_in_files(self, sample, tsv_file, metadata_file):
    allele_profile = sample['allele_profile']
    allele_list = list()
    for allele in allele_profile:
        allele_value = allele['allele_crc32']  # Maybe choose key name with a setting
        if allele_value is None:
            allele_list.append('-')
        else:
            allele_list.append(str(allele_value))
    tsv_file.write('\t'.join(allele_list))
    tsv_file.write('\n')
   
   def prepare(self, samples):
      # Create a folder for the run
      root_folder = pathlib.Path('/rt_runs')
      if not root_folder.exists():
            root_folder.mkdir()
      job_folder = pathlib.Path(root_folder, str(self.pk))
      if job_folder.exists():
            print(f"Job folder {job_folder} already exists! Reusing it.")
      else:
            job_folder.mkdir()
            print(f"Created job folder {job_folder}.")
      
      tsv_file = open(pathlib.Path(job_folder, 'allele_profiles.tsv'), 'w')
      metadata_file = open(pathlib.Path(job_folder, 'metadata.tsv'), 'w')
      
      # Get allele profile for first sample so we can define TSV header
      header_list = list()
      first_sample = next(samples)
      for allele in first_sample['allele_profile']:
            locus = allele['locus']
            if locus.endswith('.fasta'):
               locus = locus[:-6]
            header_list.append(locus)
      tsv_file.write('\t'.join(header_list))
      tsv_file.write('\n')

      # Write data for first sample to files
      self.add_sample_data_in_files(first_sample, tsv_file, metadata_file)

      # Write data for subsequent samples to files
      for sample in samples:
            self.add_sample_data_in_files(sample, tsv_file, metadata_file)
      
      tsv_file.close()
      metadata_file.close()
   
      # Set new status on job
      self.set_status('READY')