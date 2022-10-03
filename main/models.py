import pathlib

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

import requests

class DataSet(models.Model):
   species = models.CharField(max_length=20, choices=settings.ALL_SPECIES)
   owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
   name = models.CharField(max_length=40, unique=True)
   created_at = models.DateTimeField(auto_now_add=True)
   modified_at = models.DateTimeField(auto_now=True)
   description = models.CharField(max_length=200, blank=True)
   mongo_keys = models.JSONField(blank=True, default=list)
   
   class Meta:
      ordering = ['-modified_at']


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

   class Meta:
      ordering = ['-pk']

   STATUSES = [
        ('NEW', 'New'),
        ('READY', 'Ready'),
        ('STARTING', 'Starting'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'ReporTree successful'),
        ('ALL_DONE', 'All done'),
        ('OS_ERROR', 'OS error'),
        ('RT_ERROR', 'ReporTree error'),
        ('OBSOLETE', 'Obsolete')
   ]
   owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
   dataset = models.ForeignKey(DataSet, models.PROTECT)
   metadata_fields = ArrayField(models.CharField(max_length=25), default=get_default_metadata_fields)
   status = models.CharField(max_length=15, choices=STATUSES, default='NEW')
   pid = models.IntegerField(blank=True, null=True)
   start_time = models.DateTimeField(blank=True, null=True)
   end_time = models.DateTimeField(blank=True, null=True)
   elapsed_time = models.IntegerField(blank=True, null=True)
   error = models.TextField(blank=True, null=True)

   # The following fields are loaded from ReporTree output files
   log = models.TextField(blank=True, null=True)
   newick = models.TextField(blank=True, null=True)
   clusters = models.TextField(blank=True, null=True)
   partitions = models.TextField(blank=True, null=True)

   def get_path(self):
      return pathlib.Path(settings.REPORTREE_JOB_FOLDER, str(self.pk))
   
   def set_status(self, new_status:str):
      if new_status not in [status[0] for status in self.STATUSES]:
         raise ValueError(f"Illegal job status: {new_status}")
      self.status = new_status
      self.save()
   
   def get_status(self):
      if self.status == 'RUNNING':
         try: 
            self.load_results_from_files()
         except FileNotFoundError as e:
            pass
      return self.get_status_display()
   
   def add_sample_data_in_files(self, sample, allele_profile_file, metadata_file):
      # Allele profiles
      allele_profile = sample['allele_profile']
      line = list()
      line.append(sample['org'] + '.' + sample['name'])
      for allele in allele_profile:
         allele_value = allele['allele_crc32']  # Maybe choose key name with a setting
         if allele_value is None:
            line.append('-')
         else:
            line.append(str(allele_value))
      allele_profile_file.write('\t'.join(line))
      allele_profile_file.write('\n')

      # Metadata
      metadata_list = [ str(sample['metadata'][key]) for key in self.metadata_fields ]
      metadata_file.write('\t'.join(metadata_list))
      metadata_file.write('\n')
   
   def prepare(self, samples):
      # Create a folder for the run
      job_folder = self.get_path()
      if not job_folder.exists():
            job_folder.mkdir()
      if job_folder.exists():
            print(f"Job folder {job_folder} already exists! Reusing it.")
      else:
            job_folder.mkdir()
            print(f"Created job folder {job_folder}.")
      
      tsv_file = open(pathlib.Path(job_folder, 'allele_profiles.tsv'), 'w')
      metadata_file = open(pathlib.Path(job_folder, 'metadata.tsv'), 'w')
      
      # Get allele profile for first sample so we can define allele file header line
      allele_header_list = list()
      allele_header_list.append('ID')
      first_sample = next(samples)
      for allele in first_sample['allele_profile']:
            locus = allele['locus']
            if locus.endswith('.fasta'):
               locus = locus[:-6]
            allele_header_list.append(locus)
      tsv_file.write('\t'.join(allele_header_list))
      tsv_file.write('\n')

      # Add header line to metadata file
      metadata_file.write('\t'.join(self.metadata_fields))
      metadata_file.write('\n')
 
      # Write data for first sample to files
      self.add_sample_data_in_files(first_sample, tsv_file, metadata_file)

      # Write data for subsequent samples to files
      for sample in samples:
            self.add_sample_data_in_files(sample, tsv_file, metadata_file)
      
      tsv_file.close()
      metadata_file.close()
   
      # Set new status on job
      self.set_status('READY')

   def run(self):
      self.start_time = timezone.now()
      self.set_status('STARTING')
      self.save()
      raw_response = requests.post(f'http://reportree:7000/reportree/start_job/{self.pk}/')
      json_response = (raw_response.json())
      self.pid = json_response['pid']
      self.error = json_response['error']
      self.set_status(json_response['status'])
      if self.status == 'SUCCESS':
         self.end_time = timezone.now()
         elapsed_time = self.end_time - self.start_time
         self.elapsed_time = elapsed_time.seconds
      self.save()
   
   def load_results_from_files(self):
      job_folder = self.get_path()
      with open(pathlib.Path(job_folder, 'ReporTree_single_HC.nwk'), 'r') as f:
         self.newick = f.read()
      with open(pathlib.Path(job_folder, 'ReporTree.log'), 'r') as f:
         self.log = f.read()
      with open(pathlib.Path(job_folder, 'ReporTree_clusterComposition.tsv'), 'r') as f:
         self.clusters = f.read()
      with open(pathlib.Path(job_folder, 'ReporTree_partitions.tsv'), 'r') as f:
         self.partitions = f.read()
      self.set_status('ALL_DONE')
      self.save()