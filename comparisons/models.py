from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Calculation statuses
NODATA = "NODATA"
PENDING = "PENDING"
VALID = "VALID"
ERROR = "ERROR"
OBSOLETE = "OBSOLETE"
CALC_STATUSES = [
    (NODATA, 'No data'),
    (PENDING, 'Pending'),
    (VALID, 'Valid'),
    (ERROR, 'Request was unsuccesful'),
    (OBSOLETE, 'Obsolete'),
]

# Tree types
SINGLE = "single"
COMPLETE = "complete"
AVERAGE = "average"
TREE_TYPES = [
    (SINGLE, 'Single'),
    (COMPLETE, 'Complete'),
    (AVERAGE, 'Average'),
]

class Species(models.Model):
    name = models.CharField(max_length=40, unique=True)
    code = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "species"
    
    def __str__(self):
        return self.name



class SequenceSet(models.Model):
    # Abstract base class that defines the basics for both Comparison and Cluster
    species = models.ForeignKey(Species, models.PROTECT)
    created_by = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    sequences = ArrayField(models.CharField(max_length=30), blank=True, default=list)
   
    class Meta:
        abstract = True
        ordering = ['-pk']

    def __str__(self):
        return f"{self.pk} {self.created_by} {self.created_at}"


class Comparison(SequenceSet):
    distances = models.JSONField(blank=True, default=dict)
    always_calculate_dm = models.BooleanField(default=False)
    dm_status = models.CharField(max_length=15, choices=CALC_STATUSES, default=NODATA)
    data_fields = ArrayField(models.CharField(max_length=25), blank=True, default=list)   # default=get_default_data_fields
    field_data = models.JSONField(blank=True, default=dict)
    microreact_project = models.CharField(max_length=20, blank=True, null=True)


class Tree(models.Model):
    tree_type = models.CharField(max_length=10, choices=TREE_TYPES, default=SINGLE)
    comparison = models.ForeignKey(Comparison, on_delete=models.SET_NULL, null=True)
    newick = models.TextField(default='()')


class Cluster(SequenceSet):
    st = models.PositiveIntegerField()
    cluster_number = models.PositiveIntegerField()

    def __str__(self):
        return f"ST{self.st}#{self.cluster_number}"


class ComparisonTool(models.Model):
    ANALYSIS_TYPES = [
        ('cgmlst', 'cgMLST'),
        ('snp', 'SNP'),
    ]

    type = models.CharField(max_length=8, choices=ANALYSIS_TYPES, default='cgmlst')
    name = models.CharField(max_length=20)
    version = models.CharField(max_length=8)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'version'], name="tool_name_version_unique"),
        ]
    
    def __str__(self):
        return f"{self.name} v.{self.version} ({self.type})"


class PotentialOutbreak(models.Model):
    created_by = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    cluster = models.ForeignKey(Cluster, models.PROTECT)
    suspected_source = models.CharField(max_length=30)
    comparison = models.ManyToManyField(Comparison)
    outbreak_id = models.IntegerField(null=True, blank=True)  # 'FUDnummer' (without prefix)