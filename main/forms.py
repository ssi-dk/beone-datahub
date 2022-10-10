from django import forms
from django.conf import settings

class NewDatasetForm(forms.Form):
    species = forms.ChoiceField(label='Select species:', choices=settings.ALL_SPECIES)
    name = forms.CharField(max_length=40, label='Unique name')
    description = forms.CharField(max_length=200, required=False, label='Optional description')


class DeleteDatasetForm(forms.Form):
    confirm_name = forms.CharField(max_length=40, label='To delete dataset, confirm dataset name')


class DashboardLauncherForm(forms.Form):
    phylo = forms.BooleanField(label='Phylogeny')
    geo = forms.BooleanField(label='Geography')
    epi = forms.BooleanField(label='Epicurve')