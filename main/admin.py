from django.contrib import admin

from django.contrib import admin
from .models import UserProfile, DataSet

admin.site.register(UserProfile)
admin.site.register(DataSet)
