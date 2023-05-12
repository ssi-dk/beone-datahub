from django.contrib import admin

from comparisons.models import Species, SequenceGroup, BaseTool, Cluster, PotentialOutbreak
from comparisons.models import Comparison

class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

admin.site.register(Species, SpeciesAdmin)


class SequenceGroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'species', 'created_by', 'created_at', 'modified_at')

admin.site.register(SequenceGroup, SequenceGroupAdmin)


class BaseToolAdmin(admin.ModelAdmin):
    list_display = ('pk', 'type', 'name', 'version')

admin.site.register(BaseTool, BaseToolAdmin)


class ComparisonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comparison, ComparisonAdmin)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('pk', 'st', 'cluster_number')

admin.site.register(Cluster, ClusterAdmin)


class PotentialOutbreakAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created_by', 'created_at', 'cluster', 'suspected_source')

admin.site.register(PotentialOutbreak, PotentialOutbreakAdmin)