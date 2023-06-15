from email.policy import default
from django import forms
from django.conf import settings

class NewDatasetForm(forms.Form):
    species = forms.ChoiceField(label='Select species:', choices=settings.ALL_SPECIES)
    name = forms.CharField(max_length=40, label='Unique name')
    description = forms.CharField(max_length=200, required=False, label='Optional description')


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