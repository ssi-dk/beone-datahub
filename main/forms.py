from django import forms
from django.conf import settings

class NewDatasetForm(forms.Form):
    species = forms.ChoiceField(label='Select species:', choices=settings.ALL_SPECIES)
    name = forms.CharField(max_length=40)
    description = forms.CharField(max_length=200)