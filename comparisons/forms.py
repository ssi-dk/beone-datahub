from email.policy import default

from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from comparisons.models import Species

class NewComparisonForm(forms.Form):
    species = forms.ModelChoiceField(Species.objects.all(), label='Select species:')
    sequences = SimpleArrayField(forms.CharField(), delimiter=" ", label='Sequences (delimited by space)')


class DeleteDatasetForm(forms.Form):
    confirm_name = forms.CharField(max_length=40, label='To delete dataset, confirm dataset name')


class DashboardLauncherForm(forms.Form):
    show_phylo = forms.BooleanField(label='Show Phylogeny', initial=True)
    show_geo = forms.BooleanField(label='Show Geography', initial=True)
    show_epi = forms.BooleanField(label='Show Epicurve', initial=True)
    epi_scale = forms.ChoiceField(label='Epicurve time scale', choices=(
            ('years', 'Years'),
            ('months', 'Months'),
            ('days', 'Days')
        ))