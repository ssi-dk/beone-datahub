from django.contrib import admin

from comparisons.models import Species, SequenceSet, BaseTool, Comparison, Cluster, PotentialOutbreak

class SpeciesAdmin(admin.ModelAdmin):
    pass

admin.site.register(Species, SpeciesAdmin)


class SequenceSetAdmin(admin.ModelAdmin):
    pass

admin.site.register(SequenceSet, SequenceSetAdmin)


class BaseToolAdmin(admin.ModelAdmin):
    pass

admin.site.register(BaseTool, BaseToolAdmin)


class ComparisonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comparison, ComparisonAdmin)

class ClusterAdmin(admin.ModelAdmin):
    pass

admin.site.register(Cluster, ClusterAdmin)


class PotentialOutbreakAdmin(admin.ModelAdmin):
    pass

admin.site.register(PotentialOutbreak, PotentialOutbreakAdmin)
