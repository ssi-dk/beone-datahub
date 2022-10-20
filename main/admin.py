from django.contrib import admin

from django.contrib import admin
from main.models import DataSet, RTJob, Cluster

admin.site.register(DataSet)
admin.site.register(RTJob)
admin.site.register(Cluster)
