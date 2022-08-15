from django import forms
from django.conf import settings

# Not in use.
class SpeciesForm(forms.Form):
    choice_list = [('all', 'All')]
    for species in settings.ALL_SPECIES:
        choice_list.append(species)
    choices = tuple(choice_list)
    species = forms.ChoiceField(label='Select species:', choices=choices)