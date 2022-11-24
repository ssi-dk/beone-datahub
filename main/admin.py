from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

from main.models import DataSet, RTJob

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

# class PartitionAdmin(admin.ModelAdmin):
#     list_display = ('name', 'rt_job')

# admin.site.register(Partition, PartitionAdmin)

# class ClusterAdmin(admin.ModelAdmin):
#     list_display = ('name', 'partition')

# admin.site.register(Cluster, ClusterAdmin)



