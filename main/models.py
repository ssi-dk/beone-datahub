from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   current_species = models.CharField(max_length=20, blank=False, null=True,
	choices=settings.ALL_SPECIES)
