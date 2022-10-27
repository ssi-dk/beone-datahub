from pathlib import Path

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
   partitions = models.TextField(blank=True, null=True)

   def get_path(self):
      return Path(settings.REPORTREE_JOB_FOLDER, str(self.pk))
   
   def set_status(self, new_status:str):
      if new_status not in [status[0] for status in self.STATUSES]:
         raise ValueError(f"Illegal job status: {new_status}")
      self.status = new_status
      self.save()
   
   def get_log_path(self):
      return Path(self.get_path(), 'ReporTree.log')
   
   def get_newick_path(self):
      return Path(self.get_path(), 'ReporTree_single_HC.nwk')
   
   def get_cluster_path(self):
      return Path(self.get_path(), 'ReporTree_clusterComposition.tsv')
   
   def get_partitions_path(self):
      return Path(self.get_path(), 'ReporTree_partitions.tsv')
   
   def rt_files_exist(self):
      if Path.exists(self.get_log_path()) \
            and Path.exists(self.get_newick_path()) \
            and Path.exists(self.get_cluster_path()) \
            and Path.exists(self.get_partitions_path()):
         return True
      return False

   def update_status(self):
      if self.status == 'RUNNING':
         if self.rt_files_exist():
            self.status = 'SUCCESS'
            self.save()
      elif self.status == 'SUCCESS':
         parse_rt_output(self)
      return self.status
   
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
      if job_folder.exists():
         print(f"WARNING: Job folder {job_folder} already exists! Reusing it.")
      else:
            job_folder.mkdir()
            print(f"Created job folder {job_folder}.")
      
      tsv_file = open(Path(job_folder, 'allele_profiles.tsv'), 'w')
      metadata_file = open(Path(job_folder, 'metadata.tsv'), 'w')
      
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
      raw_response = requests.post(f'http://reportree:7000/reportree/start_job/',
         json={'job_number': self.pk, 'timeout': settings.REPORTREE_TIMEOUT})
      json_response = (raw_response.json())
      print(json_response)
      self.pid = json_response['pid']
      self.error = json_response['error']
      self.set_status(json_response['status'])
      if self.status == 'SUCCESS':
         self.end_time = timezone.now()
         elapsed_time = self.end_time - self.start_time
         self.elapsed_time = elapsed_time.seconds
      self.save()


class Partition(models.Model):
   rt_job = models.ForeignKey(RTJob, on_delete=models.CASCADE)
   name = models.CharField(max_length=30)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=['rt_job', 'name'], name='partitions_unique_constraint')
      ]


class Cluster(models.Model):
   partition = models.ForeignKey(Partition, on_delete=models.CASCADE)
   name = models.CharField(max_length=30)
   samples = models.JSONField()

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=['partition', 'name'], name='clusters_unique_constraint')
      ]


def parse_rt_output(rt_job: RTJob):
   with open(rt_job.get_log_path(), 'r') as f:
      rt_job.log = f.read()
   with open(rt_job.get_newick_path(), 'r') as f:
      rt_job.newick = f.read()
   with open(rt_job.get_partitions_path(), 'r') as f:
      rt_job.partitions = f.read()
   
   # Parse cluster report and create Cluster objects in db
   with open(rt_job.get_cluster_path(), 'r') as f:
      cluster_lines = f.readlines()
      cluster_lines = cluster_lines[1:]  # Skip header line.
   for cluster_line in cluster_lines:
      cluster_line = cluster_line.strip()
      pa, cn, clen, sam = cluster_line.split('\t')  # partition, cluster name, cluster length, samples
      cluster = Cluster(partition=pa, cluster_name=cn)
      sample_str_list = sam.split(',')
      # Transform sample_str_list to list of dicts
      sample_list = list()
      for sample_str in sample_str_list:
         elements = sample_str.split('.')
         assert len(elements) == 2
         sample_dict = {'org': elements[0], 'name': elements[1]}
         sample_list.append(sample_dict)
      cluster.samples = sample_list
      cluster.rt_job = rt_job
      # TODO Use this field or delete it from model
      cluster.allelic_distance = 1
      cluster.save()
   rt_job.set_status('ALL_DONE')
   rt_job.save()