from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

from main.models import DataSet, RTJob, Partition, Cluster

admin.site.register(DataSet)

class RTJobAdmin(admin.ModelAdmin):
    
    readonly_fields = (
        'dataset',
        'status',
        'pid',
        'start_time',
        'end_time',
        'elapsed_time',
        'error',
        'log',
        'newick'
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'10'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

admin.site.register(RTJob, RTJobAdmin)

class PartitionAdmin(admin.ModelAdmin):
    list_display = ('rt_job', 'name')

admin.site.register(Partition, PartitionAdmin)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ( 'partition', 'name')

admin.site.register(Cluster, ClusterAdmin)



