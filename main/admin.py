from django.contrib import admin
from main.models import DataSet, RTJob, Cluster

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('rt_job', 'partition', 'cluster_name')

admin.site.register(DataSet)
admin.site.register(RTJob)
admin.site.register(Cluster, ClusterAdmin)
