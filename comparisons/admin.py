from django.contrib import admin

from comparisons.models import Species, DistanceMatrix, Tree, BaseTool, Cluster, PotentialOutbreak
from comparisons.models import Comparison


class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

admin.site.register(Species, SpeciesAdmin)


class BaseToolAdmin(admin.ModelAdmin):
    list_display = ('pk', 'type', 'name', 'version')

admin.site.register(BaseTool, BaseToolAdmin)


class DistanceMatrixAdmin(admin.ModelAdmin):
    pass

admin.site.register(DistanceMatrix, DistanceMatrixAdmin)


class TreeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Tree, TreeAdmin)


class ComparisonAdmin(admin.ModelAdmin):
    readonly_fields = ('species', 'created_by', 'sequences', 'distances')

admin.site.register(Comparison, ComparisonAdmin)


class ClusterAdmin(admin.ModelAdmin):
    list_display = ('pk', 'st', 'cluster_number')

admin.site.register(Cluster, ClusterAdmin)


class PotentialOutbreakAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created_by', 'created_at', 'cluster', 'suspected_source')

admin.site.register(PotentialOutbreak, PotentialOutbreakAdmin)
