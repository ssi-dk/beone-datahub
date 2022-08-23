from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class UserProfile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   current_species = models.CharField(max_length=20, blank=False, null=True,
                                       choices=settings.ALL_SPECIES)


class DataSet(models.Model):
   species = models.CharField(max_length=20, choices=settings.ALL_SPECIES)
   owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
   name = models.CharField(max_length=40, unique=True)
   created_at = models.DateTimeField(auto_now_add=True)
   modified_at = models.DateTimeField(auto_now=True)
   description = models.CharField(max_length=200, blank=True)
   mongo_ids = ArrayField(models.CharField(max_length=24), blank=True, default=list)

   def __str__(self):
      return self.name
