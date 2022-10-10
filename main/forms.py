from django import forms
from django.conf import settings

class NewDatasetForm(forms.Form):
    species = forms.ChoiceField(label='Select species:', choices=settings.ALL_SPECIES)
    name = forms.CharField(max_length=40, label='Unique name')
    description = forms.CharField(max_length=200, required=False, label='Optional description')


class DeleteDatasetForm(forms.Form):
    confirm_name = forms.CharField(max_length=40, label='To delete dataset, confirm dataset name')


class DashboardLauncherForm(forms.Form):
    show_phylo = forms.BooleanField(label='Show Phylogeny')
    show_geo = forms.BooleanField(label='Show Geography')
    geo_bottom_x = forms.CharField(label = 'Map bottom x')
    geo_bottom_y = forms.CharField(label = 'Map bottom y')
    geo_top_x = forms.CharField(label = 'Map top x')
    geo_top_y = forms.CharField(label = 'Map top y')
    show_epi = forms.BooleanField(label='Show Epicurve')
    epi_scale = forms.ChoiceField(label='Epi scale', choices=(
        ('years', 'Years'),
        ('months', 'Months'),
        ('days', 'Days')
        ))