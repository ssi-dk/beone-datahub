from django.contrib import admin
from main.models import DataSet, RTJob, Partition, Cluster

admin.site.register(DataSet)
admin.site.register(RTJob)

class PartitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'rt_job')

admin.site.register(Partition, PartitionAdmin)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'partition')

admin.site.register(Cluster, ClusterAdmin)

