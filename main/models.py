from pathlib import Path
from datetime import datetime

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
   return settings.DEFAULT_RT_METADATA_FIELDS

def get_default_thresholds():
   return([4, 7, 14])

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
       ('OBSOLETE', 'Obsolete'),
       ('SAMPLE_ERROR', 'Sample error'),
       ('UNKNOWN', 'Unknown error'),
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

   # Command line options
   columns_summary_report = ArrayField(models.CharField(max_length=25), default=get_default_metadata_fields)
   metadata2report = ArrayField(models.CharField(max_length=25), default=get_default_metadata_fields)
   frequency_matrix = ArrayField(models.CharField(max_length=25), default=get_default_metadata_fields)
   count_matrix = ArrayField(models.CharField(max_length=25), default=get_default_metadata_fields)
   matrix_4_grapetree = models.BooleanField(default=True)
   mx_transpose = models.BooleanField(default=True)
   analysis = models.CharField(max_length=25, default='grapetree')
   threshold = ArrayField(models.IntegerField(), default=get_default_thresholds)

   # The following fields are loaded from ReporTree output files
   log = models.TextField(blank=True, null=True)
   newick = models.TextField(blank=True, null=True)

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
      return Path(self.get_path(), 'ReporTree.nwk')
   
   def get_cluster_path(self):
      return Path(self.get_path(), 'ReporTree_clusterComposition.tsv')
   
   def get_partitions_path(self):
      return Path(self.get_path(), 'ReporTree_partitions.tsv')
   
   def get_distance_matrix_path(self):
      return Path(self.get_path(), 'ReporTree_dist.tsv')

   def rt_files_exist(self):
      if Path.exists(self.get_log_path()) \
            and Path.exists(self.get_newick_path()) \
            and Path.exists(self.get_cluster_path()) \
            and Path.exists(self.get_partitions_path()) \
            and Path.exists(self.get_distance_matrix_path()):
         return True
      return False

   def rt_done(self):
      done = False
      if Path.exists(self.get_log_path()):
         with open(self.get_log_path(), 'r') as file:
            log = file.read()
            if 'ReporTree is done!' in log:
               done = True
      return done

   def update_status(self):
      if self.status == 'RUNNING':
         if self.rt_done():
            self.status = 'SUCCESS'
            self.save()
      return self.status
   
   def add_sample_data_in_files(self, sample, allele_profile_file, metadata_file):
      sample_id = f"{sample['org']}.{sample['name']}"
      # Allele profiles
      if 'allele_profile' not in sample:
         print(f"WARNING: not allele profile found in sample {sample_id}.")
         return
      allele_profile = sample['allele_profile']
      allele_line = [ sample_id ]
      for allele in allele_profile:
         allele_value = allele['allele_crc32']  # Maybe choose key name with a setting
         if allele_value is None:
            allele_line.append('-')
         else:
            allele_line.append(str(allele_value))
      allele_profile_file.write('\t'.join(allele_line))
      allele_profile_file.write('\n')

      # Metadata
      metadata_line = [ sample_id ]
      for key in self.metadata_fields:
         if key in sample['metadata']:
            metadata_line.append(str(sample['metadata'][key]))
         else:
            print(f"WARNING: metadata field {key} was not present in sample {sample_id}")
            print("An empty field will be used")
            metadata_line.append('')
      metadata_file.write('\t'.join(metadata_line))
      metadata_file.write('\n')
   
   def prepare(self, samples):
      start_time = timezone.now()
      print(f"prepare started at {self.start_time}")
      # Create a folder for the run
      job_folder = self.get_path()
      if job_folder.exists():
         print(f"WARNING: Job folder {job_folder} already exists! Reusing it.")
      else:
            job_folder.mkdir()
            print(f"Created job folder {job_folder}.")
      
      with \
      open(Path(job_folder, 'allele_profiles.tsv'), 'w') as allele_profile_file, \
      open(Path(job_folder, 'metadata.tsv'), 'w') as metadata_file:
      
         # Get allele profile for first sample so we can define allele file header line
         allele_header_line = [ 'ID' ]
         first_sample = next(samples)
         if not 'allele_profile' in first_sample:
            print("ERROR: no allele profile!")
            self.set_status('SAMPLE_ERROR')
            self.save()
            return
         
         for allele in first_sample['allele_profile']:
               locus = allele['locus']
               if locus.endswith('.fasta'):
                  locus = locus[:-6]
               allele_header_line.append(locus)
         allele_profile_file.write('\t'.join(allele_header_line))
         allele_profile_file.write('\n')

         # Add header line to metadata file
         metadata_header_line = [ 'ID' ]
         metadata_header_line.extend(self.metadata_fields)
         metadata_file.write('\t'.join(metadata_header_line))
         metadata_file.write('\n')
   
         # Write data for first sample to files
         self.add_sample_data_in_files(first_sample, allele_profile_file, metadata_file)

         # Write data for subsequent samples to files
         for sample in samples:
               self.add_sample_data_in_files(sample, allele_profile_file, metadata_file)
      
         # Set new status on job
         self.set_status('READY')
         self.save()
         elapsed_time = timezone.now() - start_time
         print(f"prepare took {elapsed_time}")

   def run(self):
      if self.status == 'READY':
         self.start_time = timezone.now()
         self.set_status('STARTING')
         self.save()
         print(f"run started at {self.start_time}")
         raw_response = requests.post(f'http://reportree:7000/reportree/start_job/',
            json={
               'job_number': self.pk,
               'timeout': settings.REPORTREE_TIMEOUT,
               'columns_summary_report': self.columns_summary_report,
               'metadata2report': self.metadata2report,
               'frequency_matrix': self.frequency_matrix,
               'count_matrix': self.count_matrix,
               'matrix_4_grapetree': self.matrix_4_grapetree,
               'mx_transpose': self.mx_transpose,
               'analysis': self.analysis,
               'threshold': [ str(thr) for thr in self.threshold ]
               }
         )
         json_response = (raw_response.json())
         print("JSON response:")
         print(json_response)
         self.pid = json_response['pid']
         self.error = json_response['error']
         self.set_status(json_response['status'])
         end_time = timezone.now()
         elapsed_time = end_time - self.start_time
         print(f"Run took {elapsed_time}")
         if self.status == 'SUCCESS':
            self.end_time = end_time
            self.elapsed_time = elapsed_time.seconds
         self.save()
      else:
         print(f"ERROR: trying to run ReporTree job {self.pk} which has status {self.status}")


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
   started_at = timezone.now()
   print(f" {started_at}: parse_rt_output started")
   with open(rt_job.get_log_path(), 'r') as f:
      rt_job.log = f.read()
   with open(rt_job.get_newick_path(), 'r') as f:
      rt_job.newick = f.read()
   
   # Parse partitions report and create Partition objects in db
   with open(rt_job.get_partitions_path(), 'r') as f:
      lines = f.readlines()
      partition_names = lines[0].strip().split('\t')
      partition_names = partition_names[1:]
      for name in partition_names:
         partition = Partition(rt_job=rt_job, name=name)
         partition.save()
      print((f" {timezone.now()}: partitions saved in db"))
   
   # Parse cluster report and create Cluster objects in db
   with open(rt_job.get_cluster_path(), 'r') as f:
      cluster_lines = f.readlines()
      cluster_lines = cluster_lines[1:]  # Skip header line.
   for cluster_line in cluster_lines:
      cluster_line = cluster_line.strip()
      pa, cl, _len, sam = cluster_line.split('\t')  # partition, cluster, cluster length, samples
      partition = Partition.objects.get(rt_job=rt_job, name=pa)
      cluster = Cluster(partition=partition, name=cl)
      sample_str_list = sam.split(',')
      # Transform sample_str_list to list of dicts
      sample_list = list()
      for sample_str in sample_str_list:
         elements = sample_str.split('.')
         assert len(elements) == 2
         sample_dict = {'org': elements[0], 'name': elements[1]}
         sample_list.append(sample_dict)
      cluster.samples = sample_list
      cluster.save()
   print((f" {timezone.now()}: clusters saved in db"))
   rt_job.set_status('ALL_DONE')
   rt_job.save()
   elapsed_time = timezone.now() - started_at
   print(f"parse_rt_output took {elapsed_time}")