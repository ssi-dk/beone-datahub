from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class UserProfile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   current_species = models.CharField(max_length=20, blank=False, null=True,
                                       choices=settings.ALL_SPECIES)


class DataSet(models.Model):
   owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
   name = models.CharField(max_length=40)
   created_at = models.DateTimeField(auto_now_add=True)
   modified_at = models.DateTimeField(auto_now=True)
   description = models.CharField(max_length=200, blank=True, null=True)
   sample_mongo_ids = ArrayField(models.CharField(max_length=12))