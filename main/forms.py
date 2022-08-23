from django import forms
from django.conf import settings

class SpeciesForm(forms.Form):
    species = forms.ChoiceField(label='Select species:', choices=settings.ALL_SPECIES)