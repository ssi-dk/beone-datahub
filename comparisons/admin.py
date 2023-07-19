from django.contrib import admin

from comparisons.models import Species, Tree, ComparisonTool, Cluster, PotentialOutbreak
from comparisons.models import Comparison, Dashboard


class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

admin.site.register(Species, SpeciesAdmin)


class BaseToolAdmin(admin.ModelAdmin):
    list_display = ('pk', 'type', 'name', 'version')

admin.site.register(ComparisonTool, BaseToolAdmin)


class TreeAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'tree_type', 'comparison', 'newick']

admin.site.register(Tree, TreeAdmin)


class ComparisonAdmin(admin.ModelAdmin):
    list_display = ('pk', 'species')
    readonly_fields = ('species', 'created_by', 'tool', 'sequences', 'dm_status', 'distances',)

admin.site.register(Comparison, ComparisonAdmin)


class DashboardAdmin(admin.ModelAdmin):
    pass

admin.site.register(Dashboard, DashboardAdmin)


class ClusterAdmin(admin.ModelAdmin):
    list_display = ('pk', 'species', 'st', 'cluster_number')

admin.site.register(Cluster, ClusterAdmin)


class PotentialOutbreakAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created_by', 'created_at', 'cluster', 'suspected_source', 'outbreak_id')

admin.site.register(PotentialOutbreak, PotentialOutbreakAdmin)
